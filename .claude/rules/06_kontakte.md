# 06 — Kontakte (Adressbuch)

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
