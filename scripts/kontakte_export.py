#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kontakte_export.py — Apple Kontakte (macOS/iCloud) -> Hub-Cache

Exportiert alle Kontakte aus der lokalen Apple-Kontakte-Datenbank nach
    module/kontakte/kontakte.csv

Warum ein Cache?
    Der Hub (und Claude) kann so IMMER auf die Kontakte zugreifen - auch in
    Cloud-Sessions und in geplanten Laeufen, in denen kein macOS-Zugriff
    moeglich ist.

Aufruf:
    python3 scripts/kontakte_export.py            # normaler Lauf
    python3 scripts/kontakte_export.py --dry-run  # nur zaehlen, nichts schreiben
    python3 scripts/kontakte_export.py --applescript   # Fallback erzwingen

Datenquellen (in dieser Reihenfolge):
    1. SQLite: ~/Library/Application Support/AddressBook/**/AddressBook-v22.abcddb
       (schnell, keine Automation-Dialoge; braucht ggf. "Festplattenvollzugriff"
        fuer das ausfuehrende Programm - bei launchd: /usr/bin/python3)
    2. Fallback AppleScript ueber Contacts.app (langsamer, braucht die
       Freigaben "Kontakte" + "Automation")

Nur Standardbibliothek. Nichts wird nach aussen gesendet.
"""

import argparse
import csv
import glob
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIEL_DIR = os.path.join(HUB, "module", "kontakte")
ZIEL_CSV = os.path.join(ZIEL_DIR, "kontakte.csv")
LOG = os.path.join(HUB, "logs", "kontakte_export.log")

ADDRESSBOOK = os.path.expanduser("~/Library/Application Support/AddressBook")

FELDER = [
    "name", "vorname", "nachname", "firma",
    "email", "email_alle", "telefon", "telefon_alle",
    "notiz", "quelle",
]


# --------------------------------------------------------------------------- #
# Hilfen
# --------------------------------------------------------------------------- #
def log(msg):
    zeile = "%s  %s" % (datetime.now().strftime("%d.%m.%Y %H:%M:%S"), msg)
    print(zeile)
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(zeile + "\n")
    except OSError:
        pass


def tel_normalisieren(nr):
    """+49 176 / 4250 8631 -> +49 176 42508631 (nur Zeichenmuell raus)."""
    if not nr:
        return ""
    nr = re.sub(r"[^\d+]", " ", nr)
    return re.sub(r"\s+", " ", nr).strip()


def spalten(con, tabelle):
    try:
        return {r[1] for r in con.execute("PRAGMA table_info(%s)" % tabelle)}
    except sqlite3.Error:
        return set()


# --------------------------------------------------------------------------- #
# Quelle 1: SQLite (AddressBook-v22.abcddb)
# --------------------------------------------------------------------------- #
def db_dateien():
    pfade = []
    for muster in (
        os.path.join(ADDRESSBOOK, "AddressBook-v22.abcddb"),
        os.path.join(ADDRESSBOOK, "Sources", "*", "AddressBook-v22.abcddb"),
    ):
        pfade.extend(sorted(glob.glob(muster)))
    return pfade


def lies_db(pfad, tmpdir):
    """Kopiert die DB (inkl. WAL) und liest sie aus. Gibt Liste von dicts."""
    ziel = os.path.join(tmpdir, "ab_%d.abcddb" % abs(hash(pfad)))
    shutil.copy2(pfad, ziel)
    for suffix in ("-wal", "-shm"):
        if os.path.exists(pfad + suffix):
            shutil.copy2(pfad + suffix, ziel + suffix)

    quelle = os.path.basename(os.path.dirname(pfad))
    if quelle == "AddressBook":
        quelle = "lokal"

    con = sqlite3.connect(ziel)
    con.text_factory = lambda b: b.decode("utf-8", "replace")
    try:
        rec_cols = spalten(con, "ZABCDRECORD")
        if not rec_cols:
            return []

        def feld(name):
            return name if name in rec_cols else "NULL"

        sql = """
            SELECT Z_PK,
                   %s AS vorname,
                   %s AS nachname,
                   %s AS firma,
                   %s AS spitzname
            FROM ZABCDRECORD
        """ % (feld("ZFIRSTNAME"), feld("ZLASTNAME"),
               feld("ZORGANIZATION"), feld("ZNICKNAME"))

        personen = {}
        for pk, vorname, nachname, firma, spitzname in con.execute(sql):
            vorname = (vorname or "").strip()
            nachname = (nachname or "").strip()
            firma = (firma or "").strip()
            spitzname = (spitzname or "").strip()
            name = (" ".join(x for x in (vorname, nachname) if x)).strip()
            if not name:
                name = firma or spitzname
            # Kontakte ohne Namen NICHT verwerfen - viele haben nur eine
            # Mailadresse; der Name wird unten daraus gebildet.
            personen[pk] = {
                "name": name, "vorname": vorname, "nachname": nachname,
                "firma": firma, "emails": [], "tel": [], "notiz": "",
                "quelle": quelle,
            }

        # E-Mails
        if spalten(con, "ZABCDEMAILADDRESS"):
            for owner, adresse in con.execute(
                    "SELECT ZOWNER, ZADDRESS FROM ZABCDEMAILADDRESS"):
                p = personen.get(owner)
                if p and adresse and adresse.strip():
                    a = adresse.strip()
                    if a not in p["emails"]:
                        p["emails"].append(a)

        # Telefonnummern
        if spalten(con, "ZABCDPHONENUMBER"):
            for owner, nummer in con.execute(
                    "SELECT ZOWNER, ZFULLNUMBER FROM ZABCDPHONENUMBER"):
                p = personen.get(owner)
                if p and nummer and nummer.strip():
                    n = tel_normalisieren(nummer)
                    if n and n not in p["tel"]:
                        p["tel"].append(n)

        # Notizen (optional)
        note_cols = spalten(con, "ZABCDNOTE")
        if {"ZCONTACT", "ZTEXT"} <= note_cols:
            for owner, text in con.execute(
                    "SELECT ZCONTACT, ZTEXT FROM ZABCDNOTE"):
                p = personen.get(owner)
                if p and text:
                    p["notiz"] = " ".join(text.split())[:300]

        # Namenlose Eintraege ueber Mail/Telefon retten, echte Leichen wegwerfen
        fertig = []
        for p in personen.values():
            if not p["name"]:
                p["name"] = (p["emails"][0] if p["emails"]
                             else (p["tel"][0] if p["tel"] else ""))
            if p["name"]:
                fertig.append(p)
        return fertig
    finally:
        con.close()


def export_sqlite():
    dateien = db_dateien()
    if not dateien:
        raise RuntimeError("Keine AddressBook-Datenbank gefunden unter %s" % ADDRESSBOOK)

    alle = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for pfad in dateien:
            try:
                treffer = lies_db(pfad, tmpdir)
                log("  %s -> %d Eintraege" % (pfad.replace(os.path.expanduser("~"), "~"), len(treffer)))
                alle.extend(treffer)
            except (sqlite3.Error, OSError, PermissionError) as e:
                log("  UEBERSPRUNGEN %s (%s)" % (pfad, e))
    if not alle:
        raise RuntimeError("SQLite-Quelle lieferte 0 Kontakte")
    return alle


# --------------------------------------------------------------------------- #
# Quelle 2: AppleScript-Fallback
# --------------------------------------------------------------------------- #
APPLESCRIPT = r'''
set AppleScript's text item delimiters to "|"
set ausgabe to {}
tell application "Contacts"
    repeat with p in people
        set vn to ""
        set nn to ""
        set fa to ""
        try
            set vn to first name of p
        end try
        try
            set nn to last name of p
        end try
        try
            set fa to organization of p
        end try
        set mails to ""
        try
            repeat with e in emails of p
                set mails to mails & (value of e) & ","
            end repeat
        end try
        set tels to ""
        try
            repeat with t in phones of p
                set tels to tels & (value of t) & ","
            end repeat
        end try
        set ende to {vn, nn, fa, mails, tels}
        set end of ausgabe to (ende as string)
    end repeat
end tell
set AppleScript's text item delimiters to linefeed
return ausgabe as string
'''


def sauber(text):
    """AppleScript liefert fuer leere Felder den Text 'missing value'."""
    text = (text or "").strip()
    if not text or text == "missing value":
        return ""
    # kommt auch mitten im Text vor, z. B. "Abdul missing value"
    text = re.sub(r"\bmissing value\b", " ", text)
    return re.sub(r"\s+", " ", text).strip(" ,;")


def export_applescript():
    log("  AppleScript-Fallback laeuft (kann bei vielen Kontakten dauern) ...")
    res = subprocess.run(["/usr/bin/osascript", "-e", APPLESCRIPT],
                         capture_output=True, text=True, timeout=900)
    if res.returncode != 0:
        raise RuntimeError("osascript: %s" % res.stderr.strip())

    personen = []
    for zeile in res.stdout.splitlines():
        teile = zeile.split("|")
        if len(teile) < 5:
            continue
        vorname, nachname, firma, mails, tels = [sauber(t) for t in teile[:5]]
        emails = [m.strip() for m in mails.split(",") if sauber(m)]
        telefone = [tel_normalisieren(t) for t in tels.split(",") if sauber(t)]
        name = (" ".join(x for x in (vorname, nachname) if x)).strip() or firma
        if not name:
            name = emails[0] if emails else ""
        if not name:
            continue
        personen.append({
            "name": name, "vorname": vorname, "nachname": nachname,
            "firma": firma,
            "emails": emails,
            "tel": [t for t in telefone if t],
            "notiz": "", "quelle": "applescript",
        })
    if not personen:
        raise RuntimeError("AppleScript lieferte 0 Kontakte")
    return personen


# --------------------------------------------------------------------------- #
# Schreiben
# --------------------------------------------------------------------------- #
def dedupe(personen):
    """Gleicher Name + gleiche erste Mail = ein Kontakt (iCloud/lokal doppelt)."""
    zusammen = {}
    for p in personen:
        key = (p["name"].lower(),
               (p["emails"][0].lower() if p["emails"] else ""),
               p["firma"].lower())
        if key in zusammen:
            ziel = zusammen[key]
            for m in p["emails"]:
                if m not in ziel["emails"]:
                    ziel["emails"].append(m)
            for t in p["tel"]:
                if t not in ziel["tel"]:
                    ziel["tel"].append(t)
            if not ziel["notiz"]:
                ziel["notiz"] = p["notiz"]
        else:
            zusammen[key] = p
    return sorted(zusammen.values(), key=lambda x: x["name"].lower())


def schreibe_csv(personen, ziel):
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    tmp = ziel + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(FELDER)
        for p in personen:
            w.writerow([
                p["name"], p["vorname"], p["nachname"], p["firma"],
                p["emails"][0] if p["emails"] else "",
                "; ".join(p["emails"][1:]),
                p["tel"][0] if p["tel"] else "",
                "; ".join(p["tel"][1:]),
                p["notiz"], p["quelle"],
            ])
    # Backup des Vorgaengers (eine Generation reicht)
    if os.path.exists(ziel):
        shutil.copy2(ziel, ziel + ".bak")
    os.replace(tmp, ziel)


def main():
    ap = argparse.ArgumentParser(description="Apple Kontakte in den Hub exportieren")
    ap.add_argument("--dry-run", action="store_true", help="nur zaehlen, nichts schreiben")
    ap.add_argument("--applescript", action="store_true", help="AppleScript-Fallback erzwingen")
    ap.add_argument("--ziel", default=ZIEL_CSV, help="Zieldatei (Standard: module/kontakte/kontakte.csv)")
    args = ap.parse_args()

    log("Kontakte-Export gestartet")
    personen = None
    if not args.applescript:
        try:
            personen = export_sqlite()
        except Exception as e:      # noqa: BLE001 - bewusst breit, dann Fallback
            log("  SQLite-Quelle nicht nutzbar: %s" % e)
    if personen is None:
        personen = export_applescript()

    personen = dedupe(personen)
    mit_mail = sum(1 for p in personen if p["emails"])
    log("  %d Kontakte, davon %d mit E-Mail" % (len(personen), mit_mail))

    if args.dry_run:
        log("Dry-Run - nichts geschrieben")
        return 0

    schreibe_csv(personen, args.ziel)
    log("Fertig -> %s" % args.ziel)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:          # noqa: BLE001
        log("FEHLER: %s" % e)
        sys.exit(1)
