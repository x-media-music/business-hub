#!/usr/bin/env python3
"""
send_email.py — Zentraler Mail-Versand via Strato SMTP (SSL).

Ersetzt das frühere Microsoft-Graph-Template. Nutzt nur die Python-Standard-
bibliothek (smtplib/email) — keine Zusatzpakete nötig.

Voraussetzung: scripts/mail.env ist befüllt (siehe mail_config_template.env).

Funktionen:
- Postfach-Wahl:  --from info | rechnung
- OWNER-GATE-Disziplin: Versand nur mit --gate-hash (MD5 des freigegebenen
  Bodys); erzwingbar via HUB_REQUIRE_GATE_HASH=1
- Office-Guard: blockt .docx/.xlsx/.pptx an Externe (außer --allow-office)
- HTML-Autoerkennung (.html oder <html>/<p> im Text) → HTML-Mail, sonst Plaintext
- Anhänge (--attach, wiederholbar)
- Logging nach logs/email_versand.log

Beispiel:
    python3 send_email.py \\
        --from rechnung \\
        --to 5cc1bdc1-...@uploadmail.datev.de \\
        --subject "Rechnungseingang 26-0148 – 593,87 EUR" \\
        --body-file entwurf.html \\
        --attach "26-0148 ... Rechnung.pdf" --allow-office \\
        --gate-hash <md5>
"""
from __future__ import annotations

import argparse
import hashlib
import imaplib
import mimetypes
import os
import re
import smtplib
import ssl
import sys
import time
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr, formatdate
from pathlib import Path

HUB_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = HUB_ROOT / "scripts" / "mail.env"
LOG_FILE = HUB_ROOT / "logs" / "email_versand.log"

OFFICE_EXT = {".docx", ".xlsx", ".pptx", ".doc", ".xls", ".ppt"}


def load_env(path: Path) -> dict[str, str]:
    if not path.exists():
        sys.exit(f"❌ Konfig fehlt: {path}\n   → cp scripts/mail_config_template.env scripts/mail.env  und Passwörter eintragen.")
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


MAILBOXES = {
    "info": "INFO",                    # info@xmedia24.com (music)
    "rechnung": "RECHNUNG",            # rechnung@xmedia24.com (music)
    "info_event": "INFO_EVENT",        # info@xmedia-event.de (event)
    "rechnung_event": "RECHNUNG_EVENT",# rechnung@xmedia-event.de (event)
}


def mailbox_creds(env: dict[str, str], box: str) -> tuple[str, str]:
    key = MAILBOXES[box]
    addr = env.get(f"MAIL_{key}_ADDRESS", "").strip()
    pw = env.get(f"MAIL_{key}_PASSWORD", "").strip()
    if not addr or not pw:
        sys.exit(f"❌ Für Postfach '{box}' fehlen Adresse oder Passwort in scripts/mail.env.")
    return addr, pw


INTERNAL_DOMAINS = ("@xmedia24.com", "@xmedia-event.de")


def is_external(recipients: list[str]) -> bool:
    return any(not any(d in r.lower() for d in INTERNAL_DOMAINS) for r in recipients)


def build_message(args, from_addr: str) -> EmailMessage:
    body = Path(args.body_file).read_text(encoding="utf-8")
    msg = EmailMessage()
    display = "Helen Sanders" if args.absender == "sekretaerin" else "Dirk Wöhrle"
    msg["From"] = formataddr((display, from_addr))
    msg["To"] = args.to
    if args.cc:
        msg["Cc"] = args.cc
    msg["Subject"] = args.subject
    msg["Date"] = formatdate(localtime=True)
    if args.importance == "high":
        msg["Importance"] = "high"
        msg["X-Priority"] = "1"

    is_html = args.body_file.lower().endswith(".html") or "<html" in body.lower() or "<p>" in body.lower()
    if is_html:
        msg.set_content("HTML-Mail — bitte in einem HTML-fähigen Client öffnen.")
        msg.add_alternative(body, subtype="html")
    else:
        msg.set_content(body)

    # Inline-Bilder (CID) an den HTML-Teil hängen — für Logos in der Signatur
    if is_html and getattr(args, "inline", None):
        html_part = msg.get_payload()[1]
        for spec in args.inline:
            cid, _, path = spec.partition("=")
            p = Path(path)
            if not p.exists():
                sys.exit(f"❌ Inline-Bild nicht gefunden: {p}")
            ctype, _ig = mimetypes.guess_type(p.name)
            maintype, subtype = (ctype.split("/", 1) if ctype else ("image", "png"))
            html_part.add_related(p.read_bytes(), maintype, subtype, cid=f"<{cid}>")

    for a in args.attach:
        p = Path(a)
        if not p.exists():
            sys.exit(f"❌ Anhang nicht gefunden: {p}")
        ctype, _ = mimetypes.guess_type(p.name)
        maintype, subtype = (ctype.split("/", 1) if ctype else ("application", "octet-stream"))
        msg.add_attachment(p.read_bytes(), maintype=maintype, subtype=subtype, filename=p.name)
    return msg


def _mailbox_line(raw) -> str:
    return raw.decode("utf-8", "replace") if isinstance(raw, (bytes, bytearray)) else str(raw)


def find_sent_folder(imap: imaplib.IMAP4_SSL) -> str | None:
    """Ermittelt den 'Gesendet'-Ordner des Postfachs (Strato: meist 'Sent')."""
    typ, data = imap.list()
    if typ != "OK" or not data:
        return None
    candidates: list[str] = []
    for raw in data:
        s = _mailbox_line(raw)
        m = re.match(r'\((?P<flags>[^)]*)\)\s+(?:"[^"]*"|NIL)\s+(?P<name>.*)$', s)
        if not m:
            continue
        flags = m.group("flags").lower()
        name = m.group("name").strip()
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
        if "\\sent" in flags:   # RFC 6154 Special-Use-Flag → sicherste Quelle
            return name
        candidates.append(name)
    for want in ("Sent", "Gesendet", "Sent Items", "Gesendete Objekte",
                 "INBOX.Sent", "INBOX.Gesendet"):
        for c in candidates:
            if c.lower() == want.lower():
                return c
    for c in candidates:   # Teiltreffer
        if "sent" in c.lower() or "gesend" in c.lower():
            return c
    return None


def save_to_sent(env: dict[str, str], from_addr: str, pw: str, msg: EmailMessage) -> str:
    """Legt eine Kopie der gesendeten Mail per IMAP im Gesendet-Ordner ab."""
    host = env.get("IMAP_HOST", "imap.strato.de")
    port = int(env.get("IMAP_PORT", "993"))
    ctx = ssl.create_default_context()
    imap = imaplib.IMAP4_SSL(host, port, ssl_context=ctx)
    try:
        imap.login(from_addr, pw)
        folder = find_sent_folder(imap) or "Sent"
        mbox = folder
        if " " in folder or not folder.isascii():
            mbox = '"%s"' % folder
        typ, resp = imap.append(mbox, r"(\Seen)",
                                imaplib.Time2Internaldate(time.time()),
                                msg.as_bytes())
        if typ != "OK":
            raise RuntimeError(f"APPEND fehlgeschlagen: {resp}")
        return folder
    finally:
        try:
            imap.logout()
        except Exception:
            pass


def log_send(from_addr: str, args, status: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(f"{ts}\t{status}\tfrom={from_addr}\tto={args.to}\tsubj={args.subject}\tattach={len(args.attach)}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Zentraler Mail-Sender via Strato SMTP")
    ap.add_argument("--from", dest="mailbox", choices=list(MAILBOXES), default="info",
                    help="Absender-Postfach: info | rechnung (music) · info_event | rechnung_event (event)")
    ap.add_argument("--to", required=True, help="Empfängeradresse(n), Komma-getrennt")
    ap.add_argument("--cc", default="")
    ap.add_argument("--subject", required=True)
    ap.add_argument("--body-file", required=True, help="Pfad zur Body-Datei (.md/.txt/.html)")
    ap.add_argument("--absender", choices=["owner", "sekretaerin"], default="owner",
                    help="Nur für Anzeigename/Log — Signatur steht im Body")
    ap.add_argument("--gate-hash", default="", help="MD5 des freigegebenen Bodys")
    ap.add_argument("--importance", choices=["normal", "high"], default="normal")
    ap.add_argument("--allow-office", action="store_true", help="Office-Anhang an Externe zulassen")
    ap.add_argument("--attach", action="append", default=[], help="Pfad zu Anhang (wiederholbar)")
    ap.add_argument("--inline", action="append", default=[], help="Inline-Bild als CID=Pfad (z. B. logo=module/signaturen/logo.png), wiederholbar")
    ap.add_argument("--dry-run", action="store_true", help="Nur zusammenbauen + prüfen, NICHT senden")
    ap.add_argument("--no-save-sent", action="store_true",
                    help="KEINE Kopie im Gesendet-Ordner ablegen (PFLICHT für Tannenbaum-/Akquise-Massmails)")
    ap.add_argument("--save-sent-only", action="store_true",
                    help="NICHT per SMTP senden, nur eine Kopie im Gesendet-Ordner ablegen (Nachtrag)")
    args = ap.parse_args()

    body_path = Path(args.body_file)
    if not body_path.exists():
        sys.exit(f"❌ Body-Datei fehlt: {body_path}")
    body_text = body_path.read_text(encoding="utf-8")

    # --- Gate-Hash-Disziplin ---
    calc = hashlib.md5(body_text.encode("utf-8")).hexdigest()
    require = os.environ.get("HUB_REQUIRE_GATE_HASH") == "1"
    if args.gate_hash:
        if args.gate_hash.lower() != calc:
            sys.exit(f"❌ Gate-Hash stimmt NICHT mit dem Body überein.\n   erwartet: {calc}\n   übergeben: {args.gate_hash}\n   → Body wurde nach der Freigabe geändert. Versand blockiert.")
    elif require:
        sys.exit(f"❌ HUB_REQUIRE_GATE_HASH=1: --gate-hash Pflicht.\n   MD5 des aktuellen Bodys: {calc}")

    # --- Office-Guard ---
    recips = [r.strip() for r in (args.to + "," + args.cc).split(",") if r.strip()]
    if is_external(recips) and not args.allow_office:
        for a in args.attach:
            if Path(a).suffix.lower() in OFFICE_EXT:
                sys.exit(f"❌ Office-Anhang an Externe blockiert: {a}\n   → als PDF senden oder --allow-office setzen.")

    env = load_env(ENV_FILE)
    from_addr, pw = mailbox_creds(env, args.mailbox)
    smtp_host = env.get("SMTP_HOST", "smtp.strato.de")
    smtp_port = int(env.get("SMTP_PORT", "465"))

    msg = build_message(args, from_addr)

    if args.dry_run:
        print("🧪 DRY-RUN — nicht gesendet.")
        print(f"   Postfach: {args.mailbox} ({from_addr})")
        print(f"   An:       {args.to}")
        print(f"   Betreff:  {args.subject}")
        print(f"   Anhänge:  {len(args.attach)}")
        print(f"   MD5-Body: {calc}")
        return 0

    # --- Nachtrag-Modus: nur Gesendet-Kopie ablegen, NICHT per SMTP senden ---
    if args.save_sent_only:
        try:
            folder = save_to_sent(env, from_addr, pw, msg)
        except Exception as exc:  # noqa: BLE001
            log_send(from_addr, args, f"SENT-COPY-ONLY-FEHLER: {exc}")
            sys.exit(f"❌ Konnte keine Kopie im Gesendet-Ordner ablegen: {exc}")
        log_send(from_addr, args, f"SENT-COPY-ONLY:{folder}")
        print(f"📬 Kopie im Gesendet-Ordner '{folder}' von {from_addr} abgelegt (nicht per SMTP versendet).")
        return 0

    all_recips = recips
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=ctx) as srv:
            srv.login(from_addr, pw)
            srv.send_message(msg, from_addr=from_addr, to_addrs=all_recips)
    except Exception as exc:  # noqa: BLE001
        log_send(from_addr, args, f"FEHLER: {exc}")
        sys.exit(f"❌ Versand fehlgeschlagen: {exc}")

    log_send(from_addr, args, "OK")
    print(f"✅ Gesendet ab {from_addr} an {args.to}  (Betreff: {args.subject})")

    # --- Kopie in den Gesendet-Ordner (außer bei Tannenbaum-/Akquise-Mails) ---
    if not args.no_save_sent:
        try:
            folder = save_to_sent(env, from_addr, pw, msg)
            log_send(from_addr, args, f"SENT-COPY:{folder}")
            print(f"📬 Kopie im Gesendet-Ordner '{folder}' abgelegt.")
        except Exception as exc:  # noqa: BLE001 — Mail ist zugestellt, Kopie ist Nebensache
            log_send(from_addr, args, f"SENT-COPY-FEHLER: {exc}")
            print(f"⚠️  Mail wurde gesendet, aber Kopie im Gesendet-Ordner fehlgeschlagen: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
