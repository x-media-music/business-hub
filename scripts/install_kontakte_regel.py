#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install_kontakte_regel.py — legt .claude/rules/06_kontakte.md an

Nur noetig, weil die Cowork-Cloud-Session nicht in .claude/ schreiben darf.
Aufruf (im Hub-Ordner):
    python3 scripts/install_kontakte_regel.py
Ein vorhandener Stand wird vorher als .bak-JJJJMMTT-HHMM gesichert.
"""

import os
import shutil
from datetime import datetime

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIEL = os.path.join(HUB, ".claude", "rules", "06_kontakte.md")

REGEL = r"""# 06 — Kontakte (Adressbuch)

**Gilt bei:** „schreib an …", „Mail an …", „Nummer von …", Adresse, Kontaktdaten,
Adressbuch, Ansprechpartner.

## Nachschlagen — immer zuerst der Cache

```bash
python3 scripts/kontakt.py "Falk Gruber"
```

- Unscharfe Suche: Reihenfolge, Gross-/Kleinschreibung und Umlaute egal.
- `--json` für maschinenlesbare Ausgabe, `--limit N` für mehr Treffer,
  `--mit-mail` nur Kontakte mit Mailadresse.
- **Nie eine Adresse raten oder aus dem Gedächtnis rekonstruieren.**

## Entscheidungsbaum

| Ergebnis | Vorgehen |
|---|---|
| **Genau 1 Treffer** | Adresse übernehmen, Entwurf bauen |
| **Mehrere Treffer** | Kurz auflisten und Dirk wählen lassen — nicht raten |
| **Kein Treffer** | 1. Cache-Alter prüfen (`--stand`) · 2. wenn Mac-Session: Kontakte-MCP live abfragen · 3. sonst Dirk fragen |
| **Cache älter als 3 Tage** | Im Chat erwähnen und `python3 scripts/kontakte_export.py` vorschlagen |

## Mehrere Mailadressen — welche gilt?

`kontakt.py` markiert die Hauptadresse mit `*`: die Adresse mit dem meisten
Schriftverkehr (gesendete Mails zählen doppelt), Stand aus `module/kontakte/mailverkehr.csv`.

- **Diese Adresse verwenden**, die anderen nur nennen, wenn sie plausibler ist
  (z. B. Rechnung an die Buchhaltungsadresse statt an den Ansprechpartner).
- Steht der Kontakt in `module/kontakte/hauptadressen.csv`, gewinnt dieser Eintrag immer.
- Sagt Dirk „nimm künftig die andere Adresse", Eintrag in `hauptadressen.csv` ergänzen.
- Ist zu einer Adresse kein Verkehr erfasst, im Entwurf kurz erwähnen.
- Neu auswerten: `python3 scripts/mailverkehr_index.py` (liest alle Postfächer read-only).

## Danach

1. Mail-Entwurf **im Volltext im Chat** zeigen (plus Datei), nie nur den Pfad nennen.
2. Signatur nach Kontext wählen — Booking-/Agentur-Mails immer von `info@xmedia24.com`
   mit Music-Signatur (siehe `00_core.md`).
3. **OWNER-GATE:** gefundene Adresse ist keine Sendefreigabe. Versand erst nach
   Dirks „Ja" / „senden" / „raus damit" über `scripts/send_email.py`.

## Datenschutz

Kontaktdaten bleiben lokal: `module/kontakte/` ist gitignored, Inhalte nicht in
Dokumente, Exporte oder Mails übernehmen, die nach außen gehen.

## Hintergrund

Cache-Aufbau, launchd-Job, macOS-Freigaben, Kontakte-MCP:
`wissensbasis/A/Apple-Kontakte-Setup.md` · Modul-Übersicht: `module/kontakte/README.md`
"""


def main():
    os.makedirs(os.path.dirname(ZIEL), exist_ok=True)
    if os.path.exists(ZIEL):
        sicherung = ZIEL + datetime.now().strftime(".bak-%Y%m%d-%H%M")
        shutil.copy2(ZIEL, sicherung)
        print("Vorheriger Stand gesichert:", sicherung)
    with open(ZIEL, "w", encoding="utf-8") as f:
        f.write(REGEL)
    print("Angelegt:", ZIEL)
    print("%d Zeichen geschrieben." % len(REGEL))


if __name__ == "__main__":
    main()
