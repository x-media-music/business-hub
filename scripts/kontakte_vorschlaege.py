#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kontakte_vorschlaege.py — Wer fehlt im Adressbuch?

Vergleicht den Mailverkehr (module/kontakte/mailverkehr.csv) mit den Kontakten
(module/kontakte/kontakte.csv) und schlaegt vor, wen man anlegen sollte:
Adressen mit echtem Schriftverkehr, zu denen es keine Kontaktkarte gibt.

    python3 scripts/kontakte_vorschlaege.py                 # Standard: ab 3 Mails
    python3 scripts/kontakte_vorschlaege.py --ab 10         # nur die haeufigen
    python3 scripts/kontakte_vorschlaege.py --seit 2026-01-01
    python3 scripts/kontakte_vorschlaege.py --alle          # ohne Rausch-Filter

Ergebnis: module/kontakte/vorschlaege_kontakte.csv
Spalte `anlegen` ankreuzen (x) — Claude legt die markierten Kontakte an.

Reine Auswertung vorhandener Dateien: kein Netz, kein Schreiben ins Adressbuch.
"""

import argparse
import csv
import os
import re
import sys
from datetime import datetime

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KONTAKTE = os.path.join(HUB, "module", "kontakte", "kontakte.csv")
VERKEHR = os.path.join(HUB, "module", "kontakte", "mailverkehr.csv")
ZIEL = os.path.join(HUB, "module", "kontakte", "vorschlaege_kontakte.csv")

# Adressen, hinter denen kein Mensch sitzt
RAUSCH = (
    "noreply", "no-reply", "donotreply", "do-not-reply", "mailer-daemon",
    "postmaster", "bounce", "newsletter", "mailing", "notification",
    "@boards.trello.com", "hubspotemail.net", "@bounce.", "@mail.",
    "service@", "support@", "billing@", "abo@", "shop@", "versand@",
    "kundenservice", "no_reply", "@paypal.", "@amazon.", "@ebay.",
    "@facebook", "@google.com", "@apple.com", "@dropbox.com", "@docusign",
    "@sendgrid", "@mailchimp", "@eventbrite", "@linkedin.com", "@xing.com",
    "uploadmail", "datev", "@news.", "wochenangebote", "kontowecker",
)

# Postfach-Adressen aus Automaten: 32-stellige Kennungen statt Namen
UUID_LOKAL = re.compile(r"^[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}$", re.I)

# Freemail: daraus laesst sich keine Firma ableiten
FREEMAIL = {
    "gmail.com", "googlemail.com", "gmx.de", "gmx.net", "web.de", "t-online.de",
    "icloud.com", "me.com", "mac.com", "yahoo.de", "yahoo.com", "aol.com",
    "hotmail.de", "hotmail.com", "outlook.de", "outlook.com", "live.de",
    "freenet.de", "arcor.de", "online.de", "posteo.de", "mailbox.org",
    "gmx.at", "a1.net", "bluewin.ch", "hispeed.ch", "sunrise.ch",
}


def lade(pfad):
    if not os.path.exists(pfad):
        sys.exit("Datei fehlt: %s" % pfad)
    with open(pfad, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def bekannte_adressen():
    raus = set()
    for z in lade(KONTAKTE):
        felder = [z.get("email", "")] + \
                 [a for a in (z.get("email_alle") or "").split(";")]
        for a in felder:
            a = (a or "").strip().lower()
            if "@" in a:
                raus.add(a)
    return raus


# Absender-Namen wie "Event | Katrin Pietsch" oder "Info - Musterfirma":
# solche Bausteine sind kein Personenname.
GENERISCH = {
    "event", "events", "info", "kontakt", "contact", "team", "buero", "büro",
    "service", "customer service", "kundenservice", "support", "office",
    "sekretariat", "vertrieb", "sales", "booking", "management", "verwaltung",
    "no reply", "newsletter", "presse", "marketing", "buchhaltung",
}


def name_aufbereiten(name, adresse):
    """'Knoedler, Mark' -> 'Mark Knoedler'; leer -> aus dem Adressteil bauen."""
    name = (name or "").strip().strip('"').strip()

    # Zusaetze abtrennen: "Felix Hentsch - DIE NEUE 107.7" / "Event | Katrin Pietsch"
    if name:
        teile = [t.strip() for t in re.split(r"\s*[|/]\s*|\s+[-–—]\s+", name) if t.strip()]
        if teile:
            gewaehlt = teile[0]
            if gewaehlt.lower() in GENERISCH and len(teile) > 1:
                gewaehlt = teile[1]
            name = gewaehlt
    if name and "@" in name and name.lower() == adresse.lower():
        name = ""
    if not name:
        lokal = adresse.split("@")[0]
        lokal = re.sub(r"[._\-]+", " ", lokal)
        lokal = re.sub(r"\d+", " ", lokal).strip()
        if len(lokal) < 3 or " " not in lokal:
            return ""                      # z. B. 'info', 'kontakt' -> lieber leer
        name = lokal.title()
    if "," in name:
        teile = [t.strip() for t in name.split(",", 1)]
        if len(teile) == 2 and all(teile):
            name = "%s %s" % (teile[1], teile[0])
    return re.sub(r"\s+", " ", name).strip()


def firma_aus_domain(adresse):
    domain = adresse.split("@")[-1].lower()
    if domain in FREEMAIL:
        return ""
    kern = domain.split(".")
    if len(kern) > 2 and kern[0] in ("mail", "smtp", "web", "www"):
        kern = kern[1:]
    return kern[0].replace("-", " ").title()


def main():
    ap = argparse.ArgumentParser(description="Fehlende Kontakte vorschlagen")
    ap.add_argument("--ab", type=int, default=3, help="ab wie vielen Mails (Standard 3)")
    ap.add_argument("--seit", help="nur Kontakt seit YYYY-MM-DD")
    ap.add_argument("--nur-gesendet", action="store_true",
                    help="nur Adressen, an die auch geschrieben wurde")
    ap.add_argument("--alle", action="store_true", help="Rausch-Filter aus")
    ap.add_argument("--top", type=int, default=0, help="nur die N wichtigsten")
    args = ap.parse_args()

    bekannt = bekannte_adressen()
    vorschlaege = []
    for z in lade(VERKEHR):
        adresse = (z.get("adresse") or "").strip().lower()
        if not adresse or adresse in bekannt:
            continue
        if not args.alle and any(m in adresse for m in RAUSCH):
            continue
        if not args.alle and UUID_LOKAL.match(adresse.split("@")[0]):
            continue
        gesendet = int(z.get("gesendet_an") or 0)
        empfangen = int(z.get("empfangen_von") or 0)
        gesamt = gesendet + empfangen
        if gesamt < args.ab:
            continue
        if args.nur_gesendet and not gesendet:
            continue
        letzter = (z.get("letzter_kontakt") or "").strip()
        if args.seit and letzter < args.seit:
            continue
        vorschlaege.append({
            "anlegen": "",
            "name": name_aufbereiten(z.get("name"), adresse),
            "firma": firma_aus_domain(adresse),
            "adresse": adresse,
            "mails": gesamt,
            "gesendet": gesendet,
            "empfangen": empfangen,
            "letzter_kontakt": letzter,
        })

    vorschlaege.sort(key=lambda v: (-(v["gesendet"] * 2 + v["empfangen"]),
                                    v["letzter_kontakt"]))
    if args.top:
        vorschlaege = vorschlaege[:args.top]

    os.makedirs(os.path.dirname(ZIEL), exist_ok=True)
    with open(ZIEL, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["anlegen", "name", "firma", "adresse",
                                          "mails", "gesendet", "empfangen",
                                          "letzter_kontakt"])
        w.writeheader()
        w.writerows(vorschlaege)

    ohne_namen = sum(1 for v in vorschlaege if not v["name"])
    print("%s  %d Vorschlaege -> %s"
          % (datetime.now().strftime("%d.%m.%Y %H:%M"), len(vorschlaege), ZIEL))
    print("   davon ohne erkennbaren Namen: %d (Spalte 'name' ergaenzen)" % ohne_namen)
    return 0


if __name__ == "__main__":
    sys.exit(main())
