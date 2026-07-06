# Changelog — Business-Hub-Starter

## 2026-07-01 — Branchennaher Ausbau (Werbe- & Musikagentur)

Aktuelle Version mit vorgebauten Fachmodulen für Agenturen mit Booking + Akquise.

### Neu: Fachmodule (leeres, funktionierendes Gerüst)
- **`01_booking.md`** — kompletter Buchungs-Workflow: Anfrage → Angebot → Vertrag → Technik/Rider → Kalender (RES/TBA/TBC + Doppelbuchungs-Schutz) → Event-Vorbereitung → Rechnung → Nachbereitung.
- **`02_akquise.md`** — **Tannenbaum-Prinzip** (Chain Reaction vor/rückwärts), Sammelkorb, 8-Phasen-Ablauf, 4-fach-Duplikat-Check, Impressum-Veredelung, Bounce-Handling, Kontaktformular-Automatik.
- **`module/akquise/kontakte/`** — leere Datenstruktur (Sammelkorb-/Bestandslisten-CSV + JSON) + Engine-README.
- **`module/booking/`** — Ablage-Gerüst (vertraege/, info_sheets/).

### Neu: `ANLEITUNG.md`
Betriebsanleitung in Du-Sprache: wie man den Hub steuert, insbesondere das Tannenbaum-Prinzip (Sammelkorb → Veredelung → Formulare → Freigabe → Bounce).

### Neu in `00_core.md`
- **7-Schritt-Methodik** — verbindlicher Arbeitsablauf pro Aufgabe
- **Gate-Hash** — optionaler MD5-Schutz zwischen Freigabe und Versand
- **Wenn-Dann-Pflicht** — jeder offene Loop bekommt sofort eine datierte Aufgabe

### Zusatz-Script
- **`wissensbasis_index.py`** — generiert die durchsuchbare Wissensbasis-Übersicht.

---

## 2026-05-12 — Mantel-Update

Mantel auf aktuellen Stand gebracht (gegenüber 24.04.2026-Version).

### Neu in `00_core.md`
- **GRÜNDLICHKEIT & MITDENKEN** — Mindset-Sektion am Anfang
- **SUPER-GEHIRN-STANDARD** — Owner-Erwartung an Claude
- **EMAIL-REGELN erweitert:** HTML-Default für externe Mails, Vornamen-Spiegeln (Hamburger Sie), keine Hintertüren in Mahn-Mails, Querprüfen vor Nachfassen
- **DOKUMENTE ZUR ANSICHT:** Cleanup-Verifikation (Original am Produktivplatz prüfen vor Verschieben/Löschen)
- **SCHREIBEN PROFESSIONELL** — eigene Sektion (PDF bei Verträgen, saubere Struktur)
- **RESPONSIVE ARBEITSWEISE** — eigene Sektion (keine langen Blockaden)

### Neu: Pre-Seed `memory/`
14 Universal-Mantel-Memories als Templates:
- Nordstern: Super-Gehirn-Standard
- Mindset & Gate: Mitdenken-Pflicht, Gate niemals impliziert, Responsive Arbeitsweise
- Externe Kommunikation: HTML, Finale Mail komplett zeigen, Keine Hintertüren, Anrede-Vornamen, Querprüfen, Schreiben professionell
- Hub-Disziplin: Ansicht-Cleanup-Verifikation, Session-Start-Pflichtprogramm, Session-Protokoll, Ende-Befehl-5-Durchgang

→ Index in `memory/MEMORY.md`. Direkt übernehmbar, anpassbar oder löschbar.

### Unverändert
- `scripts/` bleibt minimaler Template-Werkzeugkasten (Owner aktiviert nach Bedarf)
- `ONBOARDING.md` (separate Doku, Stand 24.04.2026 weiterhin gültig)
- README.md, CLAUDE.md (Skelett OK)

---

## 2026-04-24 — Erste Version (initialer Starter)
