# Modul Kontakte

Adressbuch-Anbindung des Hubs. Ziel: „Schreib eine Mail an Falk Gruber" funktioniert
ohne Rückfrage nach der Adresse.

## Inhalt

| Datei | Was |
|---|---|
| `kontakte.csv` | Cache aller Apple-/iCloud-Kontakte (Name, Firma, Mails, Telefon, Notiz) — **gitignored** |
| `kontakte.csv.bak` | Vorgänger-Stand (eine Generation) |
| `mailverkehr.csv` | je Mailadresse: wie oft gesendet/empfangen, letzter Kontakt — **gitignored** |
| `hauptadressen.csv` | manuelle Ausnahmen: Spalten `kontakt,adresse` (schlägt den Mailverkehr) |

## Bedienung

```bash
python3 scripts/kontakt.py "Falk Gruber"      # suchen (unscharf, Umlaute egal)
python3 scripts/kontakt.py gruber --json      # maschinenlesbar
python3 scripts/kontakt.py --stand            # Alter des Caches
python3 scripts/kontakte_export.py            # Cache jetzt neu ziehen
python3 scripts/mailverkehr_index.py          # Hauptadressen neu auswerten (24 Monate)
```

## Hauptadresse

Hat ein Kontakt mehrere Mailadressen, markiert `kontakt.py` die mit `*`, über die
tatsächlich kommuniziert wird — ermittelt aus dem Schriftverkehr aller Strato-Postfächer
(gesendete Mails zählen doppelt). Passt das im Einzelfall nicht, trägst du die Adresse in
`hauptadressen.csv` ein; dieser Eintrag gewinnt immer:

```csv
kontakt,adresse
Falk Gruber,fg@mediapool-stuttgart.de
```

## Ablauf

`scripts/kontakte_export.py` liest die lokale Apple-Kontakte-Datenbank
(`~/Library/Application Support/AddressBook/**`) und schreibt sie hierher.
Läuft täglich **06:45** per launchd-Job `com.xmedia.hub.kontakte`,
Log: `logs/kontakte_export.log`.

Setup, Freigaben und der zusätzliche Live-Weg (lokaler Kontakte-MCP):
`wissensbasis/A/Apple-Kontakte-Setup.md`.

## Regeln

- Kontaktdaten **bleiben lokal** — nicht ins Git-Repo, nicht in Mails/Exporte kopieren,
  die nach außen gehen.
- Bei mehreren Treffern: Claude fragt nach, statt zu raten.
- Steht ein Kontakt nicht im Cache (frisch angelegt), erst `kontakte_export.py` laufen lassen.
- OWNER-GATE bleibt: gefundene Adresse ≠ Erlaubnis zu senden.
