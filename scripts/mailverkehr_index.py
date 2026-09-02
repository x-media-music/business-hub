#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mailverkehr_index.py — Welche Adresse wird wirklich benutzt?

Zaehlt je E-Mail-Adresse, wie oft sie im Schriftverkehr vorkommt (Ein- und
Ausgang, alle Strato-Postfaecher) und wann zuletzt. Ergebnis:

    module/kontakte/mailverkehr.csv

`kontakt.py` markiert damit die **Hauptadresse** eines Kontakts — also die,
ueber die tatsaechlich kommuniziert wird, nicht die, die zufaellig zuerst in
der Kontaktkarte steht.

Aufruf:
    python3 scripts/mailverkehr_index.py                  # letzte 24 Monate, alle Postfaecher
    python3 scripts/mailverkehr_index.py --monate 12
    python3 scripts/mailverkehr_index.py --seit 2025-01-01
    python3 scripts/mailverkehr_index.py --postfach info --postfach anfrage

Liest **read-only** (markiert nichts als gelesen) und laedt nur Kopfzeilen —
keine Mailtexte, keine Anhaenge. Zugangsdaten kommen aus scripts/mail.env.
"""

import argparse
import csv
import imaplib
import os
import sys
from datetime import datetime, timedelta
from email import message_from_bytes
from email.header import decode_header, make_header
from email.utils import getaddresses, parsedate_to_datetime
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
ENV_FILE = HUB / "scripts" / "mail.env"
ZIEL = HUB / "module" / "kontakte" / "mailverkehr.csv"
LOG = HUB / "logs" / "mailverkehr_index.log"

# gleiche Namen wie in check_inbox.py
MAILBOXES = {
    "info": "INFO",
    "rechnung": "RECHNUNG",
    "info_event": "INFO_EVENT",
    "rechnung_event": "RECHNUNG_EVENT",
    "ninox": "NINOX",
    "anfrage": "ANFRAGE",
}
SENT_KANDIDATEN = ("Sent Items", "Sent", "Gesendet", "INBOX.Sent")

# Absender, die keine Ansprechpartner sind
MUELL = ("noreply", "no-reply", "donotreply", "do-not-reply", "mailer-daemon",
         "postmaster", "bounce", "notifications@", "newsletter@", "mailings@")

CHUNK = 300


def log(msg):
    zeile = "%s  %s" % (datetime.now().strftime("%d.%m.%Y %H:%M:%S"), msg)
    print(zeile, flush=True)
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(zeile + "\n")
    except OSError:
        pass


def load_env(path):
    if not path.exists():
        sys.exit("Konfig fehlt: %s" % path)
    env = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def dec(value):
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value)))
    except Exception:      # noqa: BLE001
        return value


def imap_date(d):
    return d.strftime("%d-%b-%Y")


def adressen(kopfzeilen):
    """['Falk Gruber <fg@x.de>', ...] -> [('Falk Gruber', 'fg@x.de'), ...]"""
    raus = []
    for name, adresse in getaddresses([k for k in kopfzeilen if k]):
        adresse = (adresse or "").strip().lower()
        if "@" not in adresse or adresse.startswith("@") or adresse.endswith("@"):
            continue
        if any(m in adresse for m in MUELL):
            continue
        raus.append((dec(name).strip(' "'), adresse))
    return raus


def scanne(box, env, seit, statistik, eigene):
    key = MAILBOXES[box]
    addr = env.get("MAIL_%s_ADDRESS" % key, "").strip()
    pw = env.get("MAIL_%s_PASSWORD" % key, "").strip()
    if not addr or not pw:
        log("  %s: keine Zugangsdaten in mail.env - uebersprungen" % box)
        return
    eigene.add(addr.lower())

    host = env.get("IMAP_HOST", "imap.strato.de")
    port = int(env.get("IMAP_PORT", "993"))
    try:
        M = imaplib.IMAP4_SSL(host, port)
        M.login(addr, pw)
    except Exception as exc:       # noqa: BLE001
        log("  %s: Login fehlgeschlagen (%s)" % (box, exc))
        return

    try:
        typ, boxes = M.list()
        vorhanden = set()
        if typ == "OK":
            for b in boxes or []:
                vorhanden.add(b.decode(errors="replace").split(' "." ')[-1].strip().strip('"'))

        ordner = [("inbox", "INBOX")]
        for kandidat in SENT_KANDIDATEN:
            if kandidat in vorhanden:
                ordner.append(("sent", kandidat))
                break

        for rolle, name in ordner:
            try:
                typ, _ = M.select('"%s"' % name, readonly=True)
                if typ != "OK":
                    log("  %s/%s: nicht lesbar" % (box, rolle))
                    continue
                typ, data = M.uid("search", None, "SINCE", imap_date(seit))
                if typ != "OK":
                    continue
                uids = [x.decode() for x in data[0].split()]
                log("  %s/%s: %d Mails" % (box, rolle, len(uids)))

                for i in range(0, len(uids), CHUNK):
                    teil = ",".join(uids[i:i + CHUNK])
                    typ, mdata = M.uid(
                        "fetch", teil,
                        "(BODY.PEEK[HEADER.FIELDS (FROM TO CC DATE)])")
                    if typ != "OK":
                        continue
                    for eintrag in mdata or []:
                        if not isinstance(eintrag, tuple) or len(eintrag) < 2:
                            continue
                        m = message_from_bytes(eintrag[1])
                        try:
                            wann = parsedate_to_datetime(m.get("Date"))
                            datum = wann.strftime("%Y-%m-%d")
                        except Exception:      # noqa: BLE001
                            datum = ""
                        if rolle == "sent":
                            paare = adressen([m.get("To"), m.get("Cc")])
                            richtung = "gesendet"
                        else:
                            paare = adressen([m.get("From")])
                            richtung = "empfangen"
                        for name_txt, adresse in paare:
                            e = statistik.setdefault(adresse, {
                                "adresse": adresse, "name": "", "gesendet": 0,
                                "empfangen": 0, "letzter": "", "postfaecher": set()})
                            e[richtung] += 1
                            e["postfaecher"].add(box)
                            if name_txt and not e["name"]:
                                e["name"] = name_txt
                            if datum > e["letzter"]:
                                e["letzter"] = datum
            except Exception as exc:           # noqa: BLE001
                log("  %s/%s: Fehler (%s)" % (box, rolle, exc))
    finally:
        try:
            M.logout()
        except Exception:      # noqa: BLE001
            pass


def main():
    ap = argparse.ArgumentParser(description="Mailverkehr je Adresse auswerten")
    ap.add_argument("--monate", type=int, default=24, help="Zeitraum in Monaten (Standard 24)")
    ap.add_argument("--seit", help="Startdatum YYYY-MM-DD (schlaegt --monate)")
    ap.add_argument("--postfach", action="append", choices=list(MAILBOXES),
                    help="nur dieses Postfach (mehrfach moeglich; Standard: alle)")
    args = ap.parse_args()

    seit = (datetime.strptime(args.seit, "%Y-%m-%d") if args.seit
            else datetime.now() - timedelta(days=int(args.monate * 30.44)))
    boxen = args.postfach or list(MAILBOXES)

    log("Mailverkehr-Index gestartet (seit %s, Postfaecher: %s)"
        % (seit.strftime("%d.%m.%Y"), ", ".join(boxen)))

    env = load_env(ENV_FILE)
    statistik, eigene = {}, set()
    for box in boxen:
        scanne(box, env, seit, statistik, eigene)

    for adresse in list(statistik):
        if adresse in eigene:
            del statistik[adresse]

    zeilen = sorted(statistik.values(),
                    key=lambda e: (-(e["gesendet"] * 2 + e["empfangen"]), e["letzter"]),
                    reverse=False)

    ZIEL.parent.mkdir(parents=True, exist_ok=True)
    with open(ZIEL, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["adresse", "name", "gesendet_an", "empfangen_von", "gesamt",
                    "letzter_kontakt", "postfaecher"])
        for e in zeilen:
            w.writerow([e["adresse"], e["name"], e["gesendet"], e["empfangen"],
                        e["gesendet"] + e["empfangen"], e["letzter"],
                        ";".join(sorted(e["postfaecher"]))])

    log("%d Adressen -> %s" % (len(zeilen), ZIEL))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("Abgebrochen")
        sys.exit(1)
    except Exception as e:        # noqa: BLE001
        log("FEHLER: %s" % e)
        sys.exit(1)
