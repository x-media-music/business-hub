#!/usr/bin/env python3
"""
check_inbox.py — Inkrementeller Inbox-Check via Strato IMAP (SSL).

Ersetzt das frühere Microsoft-Graph-Template. Nur Standardbibliothek
(imaplib/email) — keine Zusatzpakete.

Voraussetzung: scripts/mail.env ist befüllt (siehe mail_config_template.env).

- Liest READ-ONLY (markiert NICHTS als gelesen).
- Cursor je Postfach in backups/inbox_state.json (letzte UID) → "neue seit
  letztem Mal".
- Zeitraum-Modus (--since / --between) lässt den Cursor unangetastet.
- Optional Anhänge speichern (--save-attachments ORDNER) — ideal für rechnung@.
- Hard-Limit: max. 50 Mails pro Aufruf.

Beispiele:
    python3 check_inbox.py --from rechnung
    python3 check_inbox.py --from info --since 2026-06-01
    python3 check_inbox.py --from rechnung --save-attachments module/buchhaltung/eingang
    python3 check_inbox.py --from rechnung --cursor-show
    python3 check_inbox.py --from info --folder sent --since 2026-07-01   # Ausgang lesen
"""
from __future__ import annotations

import argparse
import imaplib
import json
import re
import sys
from datetime import datetime
from email import message_from_bytes
from email.header import decode_header, make_header
from pathlib import Path

HUB_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = HUB_ROOT / "scripts" / "mail.env"
STATE_FILE = HUB_ROOT / "backups" / "inbox_state.json"
MAX_MAILS = 50


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

# Auswählbare IMAP-Ordner. "sent" = Strato-Gesendet-Ordner "Sent Items"
# (der aktive Ausgang; "Sent Messages" ist eine tote Altlast und wird bewusst
# NICHT verwendet). Namen mit Leerzeichen werden beim SELECT gequotet.
FOLDERS = {
    "inbox": "INBOX",
    "sent": "Sent Items",
}


def mailbox_creds(env: dict[str, str], box: str) -> tuple[str, str]:
    key = MAILBOXES[box]
    addr = env.get(f"MAIL_{key}_ADDRESS", "").strip()
    pw = env.get(f"MAIL_{key}_PASSWORD", "").strip()
    if not addr or not pw:
        sys.exit(f"❌ Für Postfach '{box}' fehlen Adresse oder Passwort in scripts/mail.env.")
    return addr, pw


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def dec(value: str | None) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:  # noqa: BLE001
        return value


def imap_date(s: str) -> str:
    return datetime.strptime(s, "%Y-%m-%d").strftime("%d-%b-%Y")


def body_snippet(m, limit: int = 1600) -> str:
    """Liefert einen lesbaren Text-Auszug der Mail (Plaintext bevorzugt,
    sonst HTML grob enttaggt). Nur für die Triage — read-only."""
    text = ""
    html = ""
    for part in m.walk():
        ctype = (part.get_content_type() or "").lower()
        if part.get_content_disposition() == "attachment":
            continue
        if ctype == "text/plain" and not text:
            try:
                text = part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", "replace")
            except Exception:  # noqa: BLE001
                pass
        elif ctype == "text/html" and not html:
            try:
                html = part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", "replace")
            except Exception:  # noqa: BLE001
                pass
    raw = text or html
    if not raw:
        return ""
    if not text and html:   # HTML grob in Text wandeln
        raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
        raw = re.sub(r"(?s)<[^>]+>", " ", raw)
        raw = (raw.replace("&nbsp;", " ").replace("&amp;", "&")
                  .replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'"))
    raw = re.sub(r"[ \t]+", " ", raw)
    raw = re.sub(r"\n\s*\n\s*\n+", "\n\n", raw).strip()
    return raw[:limit] + (" …[gekürzt]" if len(raw) > limit else "")


def main() -> int:
    ap = argparse.ArgumentParser(description="Inkrementeller Inbox-Check via Strato IMAP")
    ap.add_argument("--from", dest="mailbox", choices=list(MAILBOXES), default="info")
    ap.add_argument("--folder", choices=list(FOLDERS), default="inbox", help="Ordner: inbox (Posteingang, Default) oder sent (Ausgang 'Sent Items')")
    ap.add_argument("--since", help="Ab Datum YYYY-MM-DD (Cursor unangetastet)")
    ap.add_argument("--between", help="Zeitraum YYYY-MM-DD..YYYY-MM-DD")
    ap.add_argument("--save-attachments", metavar="DIR", help="Anhänge in diesen Ordner speichern")
    ap.add_argument("--with-body", action="store_true", help="Text-Auszug jeder Mail mit ausgeben (für Triage)")
    ap.add_argument("--top", type=int, default=MAX_MAILS)
    ap.add_argument("--cursor-show", action="store_true")
    ap.add_argument("--cursor-reset", action="store_true")
    ap.add_argument("--cursor-name", default="", help="Eigener Cursor-Name (z. B. 'monitor'), damit mehrere Tasks unabhängig 'neue seit letztem Mal' verfolgen")
    args = ap.parse_args()

    state = load_state()
    box = args.mailbox
    folder = args.folder
    # Cursor-Basis: inbox behält den alten Schlüssel (rückwärtskompatibel),
    # andere Ordner (z. B. sent) bekommen einen eigenen, damit Ein- und
    # Ausgangs-Scans sich nicht gegenseitig überschreiben.
    base = box if folder == "inbox" else f"{box}~{folder}"
    skey = f"{base}#{args.cursor_name}" if args.cursor_name else base   # eigener Cursor je Task

    if args.cursor_show:
        print(f"Cursor {skey}: letzte UID = {state.get(skey, {}).get('last_uid', '—')}")
        return 0
    if args.cursor_reset:
        state.pop(skey, None)
        save_state(state)
        print(f"Cursor {skey} zurückgesetzt.")
        return 0

    env = load_env(ENV_FILE)
    addr, pw = mailbox_creds(env, box)
    host = env.get("IMAP_HOST", "imap.strato.de")
    port = int(env.get("IMAP_PORT", "993"))

    try:
        M = imaplib.IMAP4_SSL(host, port)
        M.login(addr, pw)
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"❌ IMAP-Login fehlgeschlagen ({addr}): {exc}")

    try:
        imap_folder = FOLDERS[folder]
        # Ordnernamen mit Leerzeichen (z. B. "Sent Items") müssen gequotet werden.
        M.select(f'"{imap_folder}"', readonly=True)  # readonly → markiert nichts als gelesen

        incremental = not (args.since or args.between)
        last_uid = int(state.get(skey, {}).get("last_uid", 0)) if incremental else 0

        if args.between:
            a, b = args.between.split("..")
            criteria = ["SINCE", imap_date(a), "BEFORE", imap_date(b)]
        elif args.since:
            criteria = ["SINCE", imap_date(args.since)]
        elif last_uid:
            criteria = [f"UID {last_uid + 1}:*"]
        else:
            criteria = ["ALL"]

        typ, data = M.uid("search", None, *criteria)
        if typ != "OK":
            sys.exit(f"❌ IMAP-Suche fehlgeschlagen: {typ}")
        uids = [int(x) for x in data[0].split()]
        if incremental and last_uid:
            uids = [u for u in uids if u > last_uid]
        uids = sorted(uids)
        total = len(uids)
        uids = uids[-args.top:] if total > args.top else uids

        save_dir = None
        if args.save_attachments:
            save_dir = (HUB_ROOT / args.save_attachments) if not Path(args.save_attachments).is_absolute() else Path(args.save_attachments)
            save_dir.mkdir(parents=True, exist_ok=True)

        icon = "📤" if folder == "sent" else "📥"
        label = f"{box}/{folder}" if folder != "inbox" else box
        print(f"{icon} Postfach {label} ({addr}) — {total} Treffer, zeige {len(uids)} (Limit {args.top}).")
        print("-" * 72)

        saved = 0
        for uid in uids:
            need_full = bool(save_dir) or args.with_body
            fetch_part = "(BODY.PEEK[])" if need_full else "(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE)])"
            typ, mdata = M.uid("fetch", str(uid), fetch_part)
            if typ != "OK" or not mdata or mdata[0] is None:
                continue
            raw = mdata[0][1]
            m = message_from_bytes(raw)
            frm = dec(m.get("From"))
            to = dec(m.get("To"))
            subj = dec(m.get("Subject"))
            date = dec(m.get("Date"))
            # Im Ausgang ist "An:" die relevante Spalte, sonst "Von:".
            party = f"   An:      {to}" if folder == "sent" else f"   Von:     {frm}"
            print(f"UID {uid} | {date}\n{party}\n   Betreff: {subj}")

            if args.with_body:
                snip = body_snippet(m)
                if snip:
                    indented = "\n".join("   | " + ln for ln in snip.splitlines())
                    print(f"   Text:\n{indented}")

            if save_dir:
                for part in m.walk():
                    fn = part.get_filename()
                    if not fn:
                        continue
                    fn = dec(fn)
                    disp = part.get_content_disposition()
                    ctype = (part.get_content_type() or "").lower()
                    # Echte Anhänge IMMER; zusätzlich Inline-PDFs (z. B. Musiker-
                    # rechnungen, die inline verschickt werden). Inline-Bilder
                    # (Signaturen/Logos) NICHT ziehen.
                    is_pdf = ctype == "application/pdf" or fn.lower().endswith(".pdf")
                    if disp == "attachment" or is_pdf:
                        target = save_dir / fn
                        target.write_bytes(part.get_payload(decode=True) or b"")
                        saved += 1
                        tag = "📎" if disp == "attachment" else "📎(inline)"
                        print(f"   {tag} gespeichert: {target}")
            print("-" * 72)

        if incremental and uids:
            state.setdefault(skey, {})["last_uid"] = max(uids)
            state[skey]["last_check"] = datetime.now().isoformat(timespec="seconds")
            save_state(state)

        if save_dir:
            print(f"Anhänge gespeichert: {saved} → {save_dir}")
    finally:
        try:
            M.logout()
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
