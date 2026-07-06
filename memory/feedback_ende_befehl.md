---
name: Ende-Befehl — 5-Durchgang-Prozedur für sauberen Session-Abschluss
description: Komplette Prozedur für den "Ende"-Befehl — 5 Durchgänge (Wissensbasis, MEMORY, Gegenprüfung, Optimierung, system_check) + Scripts + Protokoll löschen.
type: feedback
---
**Regel:** Wenn der Owner "Ende" schreibt, läuft folgende Komplett-Prozedur — Leitsatz: **"nichts darf verloren gehen"**.

## Die 5 Durchgänge (in dieser Reihenfolge)

### Durchgang 1 — Wissensbasis
- Alle Kontakte/Projekte/Themen, über die heute gesprochen wurde, durchgehen
- Bestehende Wissensbasis-Einträge aktualisieren (**Wegweiser-Prinzip**: WO liegt was, WER ist zuständig, WAS ist der letzte Stand — keine Inhalts-Verdopplung, kein Vertragstext, kein Email-Body)
- Neue Einträge anlegen wenn Kontakt/Projekt neu ist
- Keine Einträge löschen — Wissensbasis wächst nur
- Index wird in Durchgang 5 neu generiert (`wissensbasis_index.py`)

### Durchgang 2 — MEMORY.md (projektlokal)
- Projektlokale `MEMORY.md` aktualisieren — **nicht** die Auto-Memory-MEMORY.md!
- **Header:** Datum + kurze Session-Zusammenfassung
- **Offene Vorgänge:** neue "Antworten-abwarten", erledigte Punkte rausstreichen/✅, Termine + Fristen prüfen
- **Statusänderungen** aus den einzelnen Arbeitsbereichen einpflegen
- **Aktueller Session-Block:** was wurde heute gemacht, welche Bugs gefixt, welche Emails raus
- **Email-Zähler** für heute

### Durchgang 3 — Gegenprüfung
- Stimmen alle Dokus überein? (MEMORY.md, Wissensbasis, Rules, Templates)
- Widerspricht sich nichts zwischen den Regel-Dateien und Memory-Regeln?
- Ist jedes Referenz-Ziel (z.B. verlinkte Memory-Dateinamen) tatsächlich vorhanden? Wenn nicht → Durchgang 4 (anlegen oder Referenz entfernen)
- Sind die heute neu angelegten/geänderten Dateien am richtigen Platz (produktiv + ggf. Ansicht-Kopie im Staging-Ordner)?
- **Session-Protokoll prüfen** — wenn nicht vorhanden, ehrlich zur Kenntnis nehmen (war ein Fehler beim Start), NICHT rückwirkend erfinden

### Durchgang 4 — Optimierung / neue Regeln
- Was lief heute unrund? Korrekturen durch den Owner → neue Auto-Memory-Regel anlegen
- Erkennbare Lücken proaktiv schließen — nicht erst auf einen Report warten

### Durchgang 5 — System-Check (Scripts)
- `python scripts/system_check.py` — Konsistenz-Check der Hub-Struktur
- `python scripts/system_index.py` — `SYSTEM_INDEX.md` neu generieren
- `python scripts/wissensbasis_index.py` — Wissensbasis-Index refresh

## Zusätzliche Pflicht-Schritte

- **Session-Checkpoint `logs/session_checkpoint.md`:** falls vorhanden → löschen (normaler Abschluss, kein Crash)
- **Session-Protokoll `logs/session_protokoll.md`:** review + löschen (Erkenntnisse sind in MEMORY.md / Wissensbasis gelandet)

## Kurzbericht

Am Ende eine kompakte Zusammenfassung an den Owner:
- Was heute gelaufen ist (gruppiert nach Thema, Tabellen-Form)
- Emails raus (Anzahl)
- Offene Punkte für morgen
- Auffälligkeiten / Warnungen / Dinge die nicht geklappt haben

## Why

Eine Komplett-Check-Mentalität am Session-Ende — "nichts darf verloren gehen". Jede Session kann inhaltlich so viel Neues bringen, dass ohne die 5 Durchgänge Details untergehen würden (WB-Update vergessen, MEMORY nicht aktualisiert, Drift unentdeckt).

## How to apply

Bei "Ende" die 5 Durchgänge **in genau dieser Reihenfolge** abarbeiten, nicht überspringen. Durchgänge dürfen in Tool-Calls parallel laufen, aber jeder muss abgearbeitet werden. Am Ende Kurzbericht + Session-Protokoll löschen. Bei Zweifel "habe ich das wirklich durchgezogen?" — lieber einmal zu viel prüfen.
