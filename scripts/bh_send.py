#!/usr/bin/env python3
"""
bh_send.py — Hub-Auslieferung freigegebener Buchhaltungsbelege.

Modell (ab 11.08.2026): Hub fuehrt, App = Anzeige+Freigabe.
Dirk gibt in der App frei (dirk_entscheidung='freigegeben'); DIESES Script
liefert die freigegebenen, noch nicht ausgelieferten Belege aus:
  - firma=music -> Mail an die passende DATEV-Uploadmail (via send_email.py)
  - firma=event -> PDF-Kopie in den passenden Dropbox-Ordner

Idempotent: Marker ist bh_belege.verarbeitet_am (NULL = noch nicht ausgeliefert).
Nach Erfolg: verarbeitet_am=now + bh_protokoll-Eintrag.

Aufruf:
  python3 scripts/bh_send.py --dry-run     # nur anzeigen, nichts tun
  python3 scripts/bh_send.py               # ausliefern
Nur Vorbereiten ist frei; der Versand ist durch die App-Freigabe gedeckt
(= das OWNER-GATE im neuen Modell).
"""
from __future__ import annotations
import os, sys, json, ssl, glob, hashlib, subprocess, urllib.request, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
KEYS = HUB / "scripts" / "buchhaltung_keys.env"
SEND = HUB / "scripts" / "send_email.py"
TMP = HUB / "logs" / "datev_send"
TMP.mkdir(parents=True, exist_ok=True)

# DATEV-Uploadmail je Box (music) — Stand 03.08.2026 (Bank unveraendert)
DATEV_BOXES = {
    "bank":              "06aa928a-7817-4bcf-a4ef-c2185efe6c35@uploadmail.datev.de",
    "rechnungseingang":  "5cc1bdc1-f56a-4718-b6da-325b7939246d@uploadmail.datev.de",
    "kreditkarte_master":"abd46470-258e-4ebd-92d2-4c18b26fe595@uploadmail.datev.de",
    "kasse":             "868708a5-cb99-4ab3-ae70-0c71199e0f8a@uploadmail.datev.de",
    "rechnungsausgang":  "9616a328-2fcb-4f57-8df0-768c803106c7@uploadmail.datev.de",
}

def load_env(p: Path) -> dict:
    env = {}
    for ln in p.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1); env[k.strip()] = v.strip()
    return env

ENV = load_env(KEYS)
SB_URL = ENV["SUPABASE_URL"].rstrip("/")
SB_KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]

# Go-Live des Hub-fuehrt-Modells: nur Freigaben AB diesem Datum liefert der Hub aus.
# Aeltere freigegebene-aber-nicht-ausgelieferte Belege (Altlasten aus dem App/n8n-
# Betrieb) werden NICHT automatisch verschickt, sondern separat gemeldet.
HUB_GOLIVE = os.environ.get("HUB_GOLIVE") or ENV.get("HUB_GOLIVE") or "2026-08-11"

# bekannte Event-Dropbox-Zielordner (zur Normalisierung des Feldes dropbox_ordner)
XE_ORDNER = ["XE offene Eingangsrechnungen", "XE bezahlte Eingangsrechnungen/Master",
             "XE bezahlte Eingangsrechnungen", "XE Kassenbelege", "XE offene Ausgangsrechnugnen"]

def norm_ordner(val: str | None) -> str:
    v = (val or "").strip()
    for o in XE_ORDNER:
        if o in v:
            return o
    return "XE offene Eingangsrechnungen"

def sb(method: str, path: str, data=None):
    h = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": "application/json"}
    r = urllib.request.Request(SB_URL + path, data=(json.dumps(data).encode() if data is not None else None),
                               method=method, headers=h)
    try:
        with urllib.request.urlopen(r) as resp:
            b = resp.read(); return resp.status, (json.loads(b) if b else None)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")

def storage_download(storage_path: str) -> bytes:
    url = f"{SB_URL}/storage/v1/object/belege/{urllib.parse.quote(storage_path)}"
    r = urllib.request.Request(url, headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"})
    with urllib.request.urlopen(r) as resp:
        return resp.read()

def dropbox_event_base() -> Path | None:
    cands = []
    if ENV.get("HUB_DROPBOX_EVENT_BASE"): cands.append(ENV["HUB_DROPBOX_EVENT_BASE"])
    if os.environ.get("HUB_DROPBOX_EVENT_BASE"): cands.append(os.environ["HUB_DROPBOX_EVENT_BASE"])
    cands.append("/Users/dirkwoehrle/Library/CloudStorage/Dropbox/x-media EVENT GmbH/XE Buchhaltung")
    cands += sorted(glob.glob("/sessions/*/mnt/XE Buchhaltung"))
    for c in cands:
        if c and Path(c).is_dir(): return Path(c)
    return None

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def clean_name(row: dict) -> str:
    rg = (row.get("rechnungsnummer") or row.get("id","")[:8]).replace("/", "-")
    who = (row.get("absender_name") or "Beleg").split("(")[0].strip()[:40]
    for ch in '\\/:*?"<>|': who = who.replace(ch, "")
    return f"{who} {rg}.pdf".strip()

def protokoll(bid, aktion, details):
    sb("POST", "/rest/v1/bh_protokoll", {"beleg_id": bid, "aktion": aktion,
       "automatisch": False, "details": details})

def mark_done(bid, notiz_add):
    st, cur = sb("GET", f"/rest/v1/bh_belege?select=notizen&id=eq.{bid}")
    old = (cur[0].get("notizen") if isinstance(cur, list) and cur else "") or ""
    sb("PATCH", f"/rest/v1/bh_belege?id=eq.{bid}",
       {"verarbeitet_am": now_iso(), "notizen": (old + f" | {notiz_add} {now_iso()[:16]}").strip(" |")})

def send_music(row, pdf_bytes, dry) -> tuple[bool, str]:
    box = row.get("datev_kategorie")
    to = row.get("datev_email") or DATEV_BOXES.get(box)
    if not to:
        return False, f"keine DATEV-Adresse (box={box})"
    if dry:
        return True, f"[DRY] -> DATEV {box} ({to})"
    tmp_pdf = TMP / f"send_{row['id']}.pdf"; tmp_pdf.write_bytes(pdf_bytes)
    betrag = row.get("betrag_brutto"); rg = row.get("rechnungsnummer") or "-"
    body = TMP / f"body_{row['id']}.html"
    body.write_text(f"<p>Beleg zur DATEV-Verbuchung (Box: {box}).</p>"
                    f"<p>Rechnungssteller: {row.get('absender_name','')}<br>"
                    f"Rechnungsnummer: {rg}<br>Betrag brutto: {betrag} EUR<br>"
                    f"Firma: x-media music GmbH</p>", encoding="utf-8")
    gh = hashlib.md5(body.read_text(encoding="utf-8").encode()).hexdigest()
    subj = f"{row.get('absender_name','Beleg')} {rg} – {betrag} EUR – {box} (music)"
    cmd = [sys.executable, str(SEND), "--from", "rechnung", "--to", to,
           "--subject", subj, "--body-file", str(body), "--attach", str(tmp_pdf),
           "--gate-hash", gh, "--no-save-sent"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = r.returncode == 0 and "Gesendet" in (r.stdout + r.stderr)
    return ok, (f"-> DATEV {box}" if ok else f"SENDFEHLER: {(r.stdout+r.stderr)[-200:]}")

def send_event(row, pdf_bytes, dry) -> tuple[bool, str]:
    base = dropbox_event_base()
    if not base:
        return False, "Dropbox-Basis nicht gefunden (XE Buchhaltung nicht gemountet)"
    ordner = norm_ordner(row.get("dropbox_ordner"))
    ziel = base / ordner
    if not ziel.is_dir():
        return False, f"Zielordner fehlt: {ordner}"
    dest = ziel / clean_name(row)
    if dry:
        return True, f"[DRY] -> Dropbox/{ordner}/{dest.name}"
    dest.write_bytes(pdf_bytes)
    return True, f"-> Dropbox/{ordner}/{dest.name}"

def main():
    dry = "--dry-run" in sys.argv
    st, rows = sb("GET", "/rest/v1/bh_belege?select=id,firma,absender_name,rechnungsnummer,"
                  "betrag_brutto,datev_kategorie,datev_email,dropbox_ordner,pdf_storage_path,zahlungsstatus,dirk_entschieden_am"
                  f"&dirk_entscheidung=eq.freigegeben&verarbeitet_am=is.null&dirk_entschieden_am=gte.{HUB_GOLIVE}&order=firma")
    if not isinstance(rows, list):
        print("Fehler beim Laden:", rows); sys.exit(1)
    # Altlasten (vor Go-Live freigegeben, nie ausgeliefert) separat melden, NICHT senden
    sa, alt = sb("GET", "/rest/v1/bh_belege?select=firma,rechnungsnummer,absender_name,betrag_brutto,dirk_entschieden_am"
                 f"&dirk_entscheidung=eq.freigegeben&verarbeitet_am=is.null&dirk_entschieden_am=lt.{HUB_GOLIVE}&order=dirk_entschieden_am")
    if isinstance(alt, list) and alt:
        print(f"⚠ {len(alt)} ALTLASTEN (vor {HUB_GOLIVE} freigegeben, nie ausgeliefert) — NICHT automatisch verschickt:")
        for a in alt:
            print(f"    - {a.get('firma'):5} {a.get('rechnungsnummer') or '-':14} {a.get('absender_name','')[:34]:34} {a.get('betrag_brutto')} € (freigegeben {str(a.get('dirk_entschieden_am'))[:10]})")
    if not rows:
        print(f"bh_send: keine freigegebenen, unverarbeiteten Belege ab {HUB_GOLIVE}."); return
    print(f"bh_send: {len(rows)} freigegebene Belege ab {HUB_GOLIVE}{' (DRY-RUN)' if dry else ''}")
    done = fail = 0
    for row in rows:
        rg = row.get("rechnungsnummer") or row["id"][:8]
        if not row.get("pdf_storage_path"):
            print(f"  ⚠ {rg}: kein PDF im Storage — uebersprungen"); fail += 1; continue
        try:
            pdf = storage_download(row["pdf_storage_path"])
        except Exception as e:
            print(f"  ⚠ {rg}: PDF-Download-Fehler {e}"); fail += 1; continue
        if row.get("firma") == "event":
            ok, msg = send_event(row, pdf, dry)
            aktion = "verschoben"
        else:
            ok, msg = send_music(row, pdf, dry)
            aktion = "versendet"
        print(f"  {'✅' if ok else '❌'} {row.get('firma'):5} {rg:14} {msg}")
        if ok and not dry:
            mark_done(row["id"], f"Hub ausgeliefert {msg}")
            protokoll(row["id"], aktion, {"quelle": "bh_send", "ziel": msg, "box": row.get("datev_kategorie") or row.get("dropbox_ordner")})
            done += 1
        elif not ok:
            fail += 1
    if not dry:
        print(f"bh_send fertig: {done} ausgeliefert, {fail} Fehler.")

if __name__ == "__main__":
    main()
