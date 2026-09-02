#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kontakt.py — Kontakt im Hub-Cache nachschlagen

    python3 scripts/kontakt.py "Falk Gruber"
    python3 scripts/kontakt.py gruber --json
    python3 scripts/kontakt.py "hofbraeu" --limit 10
    python3 scripts/kontakt.py --stand          # nur Alter des Caches zeigen

Sucht unscharf in module/kontakte/kontakte.csv (Name, Firma, E-Mail, Telefon).
Umlaute/Gross-Klein/Reihenfolge egal: "gruber falk" findet "Falk Gruber".

Rueckgabewerte: 0 = Treffer, 1 = kein Treffer, 2 = kein Cache vorhanden.
"""

import argparse
import csv
import json
import os
import re
import sys
import unicodedata
from datetime import datetime

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PFAD = os.path.join(HUB, "module", "kontakte", "kontakte.csv")
VERKEHR_PFAD = os.path.join(HUB, "module", "kontakte", "mailverkehr.csv")
OVERRIDE_PFAD = os.path.join(HUB, "module", "kontakte", "hauptadressen.csv")


def _grund(text):
    """Kleinbuchstaben, Akzente weg, nur harmlose Zeichen."""
    text = unicodedata.normalize("NFKD", (text or "").lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9@.+ ]", " ", text)


def varianten(text):
    """Zwei Schreibweisen: 'hofbraeu' (ae) und 'hofbrau' (nur Punkte weg)."""
    ae = (text or "").lower().replace("ä", "ae").replace("ö", "oe") \
                             .replace("ü", "ue").replace("ß", "ss")
    return _grund(ae), _grund(text)


def tokens(text):
    """['falk', 'gruber'] -> [('falk',), ('gruber',)] · je Wort beide Schreibweisen."""
    ergebnis = []
    for wort in (text or "").split():
        ae, plain = varianten(wort)
        formen = tuple({f for f in (ae.strip(), plain.strip()) if f})
        if formen:
            ergebnis.append(formen)
    return ergebnis


def score(zeile, such_tokens):
    """0 = kein Treffer. Hoeher = besser."""
    def feld(*keys):
        roh = " ".join(zeile.get(k, "") or "" for k in keys)
        ae, plain = varianten(roh)
        return ae + " " + plain

    name = feld("name")
    firma = feld("firma")
    rest = feld("email", "email_alle", "telefon", "telefon_alle", "notiz")
    heuhaufen = " ".join([name, firma, rest])
    name_worte = set(name.split())
    firma_worte = set(firma.split())

    punkte = 0
    for formen in such_tokens:
        if any(t in name_worte for t in formen):
            punkte += 10                      # exaktes Namenswort
        elif any(w.startswith(t) for t in formen for w in name_worte):
            punkte += 7                       # Namensanfang
        elif any(t in firma_worte for t in formen) or \
                any(w.startswith(t) for t in formen for w in firma_worte):
            punkte += 5
        elif any(t in heuhaufen for t in formen):
            punkte += 3                       # irgendwo enthalten
        else:
            return 0                          # ein Token passt gar nicht -> raus
    if zeile.get("email"):
        punkte += 1                           # mit Mailadresse ist nuetzlicher
    return punkte


def lade(pfad):
    with open(pfad, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------------------- #
# Hauptadresse: welche Adresse wird wirklich benutzt?
# --------------------------------------------------------------------------- #
def lade_verkehr():
    """module/kontakte/mailverkehr.csv -> {adresse: {gesamt, letzter, ...}}"""
    if not os.path.exists(VERKEHR_PFAD):
        return {}
    daten = {}
    for z in lade(VERKEHR_PFAD):
        adresse = (z.get("adresse") or "").strip().lower()
        if not adresse:
            continue
        try:
            gesendet = int(z.get("gesendet_an") or 0)
            empfangen = int(z.get("empfangen_von") or 0)
        except ValueError:
            gesendet = empfangen = 0
        daten[adresse] = {
            "gesendet": gesendet, "empfangen": empfangen,
            "gesamt": gesendet + empfangen,
            "letzter": (z.get("letzter_kontakt") or "").strip(),
        }
    return daten


def lade_overrides():
    """module/kontakte/hauptadressen.csv (Spalten: kontakt,adresse) -> {name: adresse}"""
    if not os.path.exists(OVERRIDE_PFAD):
        return {}
    raus = {}
    for z in lade(OVERRIDE_PFAD):
        name = (z.get("kontakt") or "").strip().lower()
        adresse = (z.get("adresse") or "").strip()
        if name and adresse:
            raus[name] = adresse
    return raus


def adressen_rang(zeile, verkehr, overrides):
    """Alle Mailadressen des Kontakts, beste zuerst. Liste von (adresse, info)."""
    roh = [zeile.get("email", "")] + \
          [a.strip() for a in (zeile.get("email_alle", "") or "").split(";")]
    adressen, gesehen = [], set()
    for a in roh:
        a = (a or "").strip()
        if a and a.lower() not in gesehen:
            gesehen.add(a.lower())
            adressen.append(a)

    bevorzugt = overrides.get((zeile.get("name") or "").strip().lower(), "").lower()

    def sortierwert(adresse):
        v = verkehr.get(adresse.lower(), {})
        # gesendete Mails wiegen doppelt: dorthin schreibt Dirk tatsaechlich
        punkte = v.get("gesendet", 0) * 2 + v.get("empfangen", 0)
        return (adresse.lower() == bevorzugt, punkte, v.get("letzter", ""))

    adressen.sort(key=sortierwert, reverse=True)
    return [(a, dict(verkehr.get(a.lower(), {}),
                     fix=(a.lower() == bevorzugt))) for a in adressen]


def adress_hinweis(info):
    if info.get("fix"):
        teile = ["von dir festgelegt"]
    elif info.get("gesamt"):
        teile = ["%d Mail%s" % (info["gesamt"], "" if info["gesamt"] == 1 else "s")]
    else:
        return ""       # nichts bekannt -> keine Klammer anhaengen
    if info.get("letzter"):
        try:
            d = datetime.strptime(info["letzter"], "%Y-%m-%d").strftime("%d.%m.%Y")
        except ValueError:
            d = info["letzter"]
        teile.append("zuletzt %s" % d)
    return ", ".join(teile)


def stand(pfad):
    alter = datetime.now() - datetime.fromtimestamp(os.path.getmtime(pfad))
    tage = alter.days
    stunden = alter.seconds // 3600
    return "Cache-Stand: %s (%s)" % (
        datetime.fromtimestamp(os.path.getmtime(pfad)).strftime("%d.%m.%Y %H:%M"),
        ("%d Tage alt" % tage) if tage else ("%d h alt" % stunden),
    )


def main():
    ap = argparse.ArgumentParser(description="Kontakt im Hub-Cache suchen")
    ap.add_argument("suche", nargs="*", help="Name, Firma, Mail oder Nummer")
    ap.add_argument("--json", action="store_true", help="JSON statt Tabelle")
    ap.add_argument("--limit", type=int, default=5, help="max. Treffer (Standard 5)")
    ap.add_argument("--mit-mail", action="store_true", help="nur Kontakte mit E-Mail")
    ap.add_argument("--stand", action="store_true", help="nur Alter des Caches zeigen")
    args = ap.parse_args()

    if not os.path.exists(CSV_PFAD):
        print("Kein Kontakte-Cache gefunden (%s).\n"
              "Einmal ausfuehren:  python3 scripts/kontakte_export.py" % CSV_PFAD)
        return 2

    if args.stand or not args.suche:
        zeilen = lade(CSV_PFAD)
        print("%s · %d Kontakte" % (stand(CSV_PFAD), len(zeilen)))
        return 0 if args.stand else 1

    such_tokens = tokens(" ".join(args.suche))
    treffer = []
    for zeile in lade(CSV_PFAD):
        if args.mit_mail and not zeile.get("email"):
            continue
        p = score(zeile, such_tokens)
        if p:
            treffer.append((p, zeile))
    treffer.sort(key=lambda x: (-x[0], x[1].get("name", "")))
    treffer = treffer[:args.limit]

    verkehr = lade_verkehr()
    overrides = lade_overrides()

    if args.json:
        raus = []
        for _, z in treffer:
            rang = adressen_rang(z, verkehr, overrides)
            d = dict(z)
            d["hauptadresse"] = rang[0][0] if rang else ""
            d["adressen"] = [{"adresse": a, **i} for a, i in rang]
            raus.append(d)
        print(json.dumps(raus, ensure_ascii=False, indent=2))
        return 0 if treffer else 1

    if not treffer:
        print("Kein Treffer fuer '%s'. %s" % (" ".join(args.suche), stand(CSV_PFAD)))
        return 1

    for p, z in treffer:
        kopf = z["name"] + (" — %s" % z["firma"] if z.get("firma") else "")
        print(kopf)
        rang = adressen_rang(z, verkehr, overrides)
        for i, (adresse, info) in enumerate(rang):
            hinweis = adress_hinweis(info)
            hinweis = "   (%s)" % hinweis if hinweis else ""
            if i == 0:
                marke = "* Mail:" if len(rang) > 1 else "  Mail:"
                print("%s %s%s" % (marke, adresse, hinweis))
            else:
                print("    auch: %s%s" % (adresse, hinweis))
        if z.get("telefon"):
            weitere = z.get("telefon_alle", "")
            print("  Tel:  %s%s" % (z["telefon"], ("  (weitere: %s)" % weitere) if weitere else ""))
        if z.get("notiz"):
            print("  Notiz: %s" % z["notiz"])
        print()
    print(stand(CSV_PFAD))
    return 0


if __name__ == "__main__":
    try:                                  # sauber bleiben, wenn nach | head gepiped wird
        import signal
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (ImportError, AttributeError, ValueError):
        pass
    sys.exit(main())
