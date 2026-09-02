#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kontakte_pflege.py — Vorschlaege sauber ins Adressbuch bringen

Zweistufig, damit nie versehentlich Dubletten entstehen:

  1. PLAN (Standard)   python3 scripts/kontakte_pflege.py
     Vergleicht module/kontakte/vorschlaege_kontakte.csv mit den vorhandenen
     Kontakten und schreibt module/kontakte/pflegeplan.csv mit drei Aktionen:

       neu        Person gibt es nicht -> neue Karte
       ergaenzen  Person gibt es -> nur die Mailadresse anhaengen
       pruefen    aehnlicher Name (z. B. Marc/Mark Knoedler) -> Dirk entscheidet

  2. ANWENDEN         python3 scripts/kontakte_pflege.py --anwenden
     Fuehrt den Plan aus. **Rein additiv:**
       - bestehende Karten: nur `make new email` anhaengen
       - Telefonnummern, Adressen, Geburtstage, Notizen, Labels bleiben unberuehrt
       - es wird nie etwas geloescht oder ueberschrieben
     Zeilen mit Aktion `pruefen` werden uebersprungen, bis du sie in der CSV
     auf `neu` oder `ergaenzen` aenderst (Spalte `aktion`).

Weitere Schalter:
     --nur-ab N       nur Vorschlaege ab N gesendeten Mails (Standard 5)
     --zeige-script   das erzeugte AppleScript nur anzeigen, nichts ausfuehren
     --limit N        hoechstens N Aenderungen (zum Antesten)

Laeuft nur auf dem Mac (AppleScript). Vorher immer erst den Plan ansehen.
"""

import argparse
import csv
import os
import re
import subprocess
import sys
import unicodedata
from datetime import datetime

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KONTAKTE = os.path.join(HUB, "module", "kontakte", "kontakte.csv")
VORSCHLAEGE = os.path.join(HUB, "module", "kontakte", "vorschlaege_kontakte.csv")
PLAN = os.path.join(HUB, "module", "kontakte", "pflegeplan.csv")
LOG = os.path.join(HUB, "logs", "kontakte_pflege.log")

SPALTEN = ["aktion", "name", "firma", "adresse", "bestehender_kontakt",
           "mails", "gesendet", "letzter_kontakt", "hinweis"]


def log(msg):
    zeile = "%s  %s" % (datetime.now().strftime("%d.%m.%Y %H:%M:%S"), msg)
    print(zeile, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(zeile + "\n")
    except OSError:
        pass


def lade(pfad):
    if not os.path.exists(pfad):
        sys.exit("Datei fehlt: %s\n   -> vorher scripts/kontakte_vorschlaege.py laufen lassen" % pfad)
    with open(pfad, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# --------------------------------------------------------------------------- #
# Namensvergleich
# --------------------------------------------------------------------------- #
def norm(text):
    text = (text or "").lower().replace("ä", "ae").replace("ö", "oe") \
                              .replace("ü", "ue").replace("ß", "ss")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"\b(dr|prof|herr|frau|mr|mrs|ms)\b\.?", " ", text)
    return re.sub(r"[^a-z0-9 ]", " ", text).split()


def namensschluessel(name):
    teile = norm(name)
    return " ".join(teile)


def aehnlich(a, b):
    """(gleich, aehnlich) fuer zwei Namen."""
    ta, tb = norm(a), norm(b)
    if not ta or not tb:
        return False, False
    if ta == tb:
        return True, True
    # gleicher Nachname?
    if ta[-1] != tb[-1]:
        return False, False
    va, vb = (ta[0] if len(ta) > 1 else ""), (tb[0] if len(tb) > 1 else "")
    if not va or not vb:
        return False, True
    if va == vb:
        return True, True
    # Alex/Alexander, Chris/Christian: einer ist Anfang des anderen
    kurz, lang = sorted([va, vb], key=len)
    if len(kurz) >= 3 and lang.startswith(kurz):
        return False, True          # plausibel, aber nur nach Rueckfrage
    return False, True              # gleicher Nachname -> auf jeden Fall pruefen


# --------------------------------------------------------------------------- #
# Plan bauen
# --------------------------------------------------------------------------- #
def plan_bauen(ab_gesendet):
    kontakte = lade(KONTAKTE)
    bekannt_mail = {}
    for k in kontakte:
        for a in [k.get("email", "")] + (k.get("email_alle") or "").split(";"):
            a = (a or "").strip().lower()
            if "@" in a:
                bekannt_mail[a] = k["name"]

    zeilen = []
    schon_geplant = set()
    for v in lade(VORSCHLAEGE):
        adresse = (v.get("adresse") or "").strip().lower()
        if not adresse or adresse in bekannt_mail or adresse in schon_geplant:
            continue
        try:
            gesendet = int(v.get("gesendet") or 0)
        except ValueError:
            gesendet = 0
        if gesendet < ab_gesendet:
            continue

        name = (v.get("name") or "").strip()
        firma = (v.get("firma") or "").strip()
        if not name:
            name = firma            # namenlose Adressen unter der Firma fuehren
        if not name:
            continue

        aktion, bestehend, hinweis = "neu", "", ""
        for k in kontakte:
            gleich, nah = aehnlich(name, k.get("name", ""))
            if gleich:
                aktion, bestehend = "ergaenzen", k["name"]
                hinweis = "Name identisch - Adresse wird angehaengt"
                break
            if nah:
                aktion, bestehend = "pruefen", k["name"]
                hinweis = ("aehnlicher Name vorhanden - selbe Person? dann "
                           "aktion auf 'ergaenzen' setzen, sonst auf 'neu'")
                # weitersuchen: vielleicht gibt es doch eine exakte Uebereinstimmung
        schon_geplant.add(adresse)
        zeilen.append({
            "aktion": aktion, "name": name, "firma": firma, "adresse": adresse,
            "bestehender_kontakt": bestehend, "mails": v.get("mails", ""),
            "gesendet": gesendet, "letzter_kontakt": v.get("letzter_kontakt", ""),
            "hinweis": hinweis,
        })

    zeilen.sort(key=lambda z: (z["aktion"], -int(z["gesendet"] or 0)))
    os.makedirs(os.path.dirname(PLAN), exist_ok=True)
    with open(PLAN, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SPALTEN)
        w.writeheader()
        w.writerows(zeilen)

    zaehler = {}
    for z in zeilen:
        zaehler[z["aktion"]] = zaehler.get(z["aktion"], 0) + 1
    log("Plan geschrieben: %s" % PLAN)
    for a in ("neu", "ergaenzen", "pruefen"):
        log("   %-10s %d" % (a, zaehler.get(a, 0)))
    if zaehler.get("pruefen"):
        log("   -> 'pruefen'-Zeilen in der CSV entscheiden, dann --anwenden")
    return zeilen


# --------------------------------------------------------------------------- #
# Anwenden (rein additiv)
# --------------------------------------------------------------------------- #
def as_escape(text):
    return (text or "").replace("\\", "\\\\").replace('"', '\\"')


def script_neu(name, firma, adresse):
    teile = name.split()
    vorname = as_escape(teile[0] if len(teile) > 1 else "")
    nachname = as_escape(" ".join(teile[1:]) if len(teile) > 1 else name)
    eigenschaften = []
    if vorname:
        eigenschaften.append('first name:"%s"' % vorname)
    eigenschaften.append('last name:"%s"' % nachname)
    if firma:
        eigenschaften.append('organization:"%s"' % as_escape(firma))
    return '''tell application "Contacts"
    set p to make new person with properties {%s}
    make new email at end of emails of p with properties {label:"Arbeit", value:"%s"}
    save
end tell''' % (", ".join(eigenschaften), as_escape(adresse))


def script_ergaenzen(bestehend, adresse):
    """Haengt NUR eine Mailadresse an - loescht nichts."""
    return '''tell application "Contacts"
    set treffer to (every person whose name is "%s")
    if (count of treffer) is 0 then error "Kontakt nicht gefunden"
    if (count of treffer) > 1 then error "Name mehrfach vorhanden - manuell klaeren"
    set p to item 1 of treffer
    set vorhanden to false
    repeat with e in emails of p
        if (value of e as string) is "%s" then set vorhanden to true
    end repeat
    if vorhanden is false then
        make new email at end of emails of p with properties {label:"Arbeit", value:"%s"}
        save
    end if
end tell''' % (as_escape(bestehend), as_escape(adresse), as_escape(adresse))


def anwenden(limit, nur_zeigen):
    if not os.path.exists(PLAN):
        sys.exit("Kein Plan gefunden. Erst ohne --anwenden laufen lassen.")
    zeilen = lade(PLAN)
    offen = [z for z in zeilen if z["aktion"] in ("neu", "ergaenzen")]
    uebersprungen = [z for z in zeilen if z["aktion"] == "pruefen"]
    if limit:
        offen = offen[:limit]

    log("Anwenden: %d Aenderungen (%d 'pruefen' bleiben liegen)"
        % (len(offen), len(uebersprungen)))

    erledigt, fehler = [], []
    for z in offen:
        skript = (script_ergaenzen(z["bestehender_kontakt"], z["adresse"])
                  if z["aktion"] == "ergaenzen"
                  else script_neu(z["name"], z["firma"], z["adresse"]))
        if nur_zeigen:
            print("\n--- %s: %s (%s)\n%s" % (z["aktion"], z["name"], z["adresse"], skript))
            continue
        res = subprocess.run(["/usr/bin/osascript", "-e", skript],
                             capture_output=True, text=True, timeout=60)
        if res.returncode == 0:
            erledigt.append(z)
            log("   OK  %-10s %-28s %s" % (z["aktion"], z["name"][:28], z["adresse"]))
        else:
            fehler.append((z, res.stderr.strip()))
            log("   FEHLER %s (%s): %s" % (z["name"], z["adresse"], res.stderr.strip()[:120]))

    if nur_zeigen:
        return 0

    log("Fertig: %d angewendet, %d Fehler, %d zur Pruefung offen"
        % (len(erledigt), len(fehler), len(uebersprungen)))
    log("   -> danach: python3 scripts/kontakte_export.py  (Cache nachziehen)")
    return 0 if not fehler else 1


def main():
    ap = argparse.ArgumentParser(description="Vorschlaege dublettenfrei ins Adressbuch bringen")
    ap.add_argument("--anwenden", action="store_true", help="Plan ausfuehren (sonst nur planen)")
    ap.add_argument("--nur-ab", type=int, default=5, help="ab N gesendeten Mails (Standard 5)")
    ap.add_argument("--limit", type=int, default=0, help="hoechstens N Aenderungen")
    ap.add_argument("--zeige-script", action="store_true", help="AppleScript nur anzeigen")
    args = ap.parse_args()

    if args.anwenden or args.zeige_script:
        return anwenden(args.limit, args.zeige_script)
    plan_bauen(args.nur_ab)
    log("Plan pruefen, dann:  python3 scripts/kontakte_pflege.py --anwenden")
    return 0


if __name__ == "__main__":
    sys.exit(main())
