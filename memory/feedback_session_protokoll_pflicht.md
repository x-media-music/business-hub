---
name: Session-Protokoll ist Pflicht am Session-Start
description: logs/session_protokoll.md wird am Session-Start angelegt und während der Session gepflegt. Nicht optional, nicht überspringen.
type: feedback
---
**Regel:** Bei jedem Session-Start das Anlegen des Session-Protokolls (siehe Session-Start-Checkliste in `00_core.md`) ist **Pflicht**, nicht optional:

- `logs/session_protokoll.md` anlegen

**Inhalt am Anfang:**

```
# Session-Protokoll DD.MM.YYYY HH:MM

## Session-Start-Checks
- [Ergebnis]

## Verlauf
- HH:MM — [Aktion]
```

Während der Session wird stichwortartig mitgeschrieben: jede wichtige Aktion, jedes Gate, jede Entscheidung, jede Email raus, jede Datei-Änderung. Am Session-Ende wird das Protokoll im Durchgang 3 der Ende-Prozedur gereviewt und im Aufräum-Schritt gelöscht (die Erkenntnisse landen in MEMORY.md / Wissensbasis).

**Why:** Das Protokoll ist die chronologische Nachverfolgbarkeit der Session und das einzige Sicherheitsnetz, wenn die Session mitten drin abbricht (kombiniert mit `session_checkpoint.md`). Ohne Protokoll ist die Session zwar inhaltlich vielleicht sauber, aber nicht mehr rekonstruierbar.

**How to apply:**
- Das Anlegen des Protokolls ist NICHT optional. Direkt nach Uhrzeit-/Datum-Check und MEMORY.md-Lesen folgt das Anlegen des Protokolls.
- Wenn ich merke, dass ich mitten in der Session bin und das Protokoll noch nicht existiert → **sofort nachholen**, nicht aufschieben.
- Zu viele Details im Protokoll sind besser als zu wenige. Beim Ende wird eh zusammengefasst + gelöscht.
