---
name: reference_recall_system
description: "Schnellzugriff aufs GESAMTE Hub-Wissen: recall.py sucht in EINEM Aufruf über Memory + Wissensbasis + Logs + Akten. Bei jeder Stand-/Wissensfrage ZUERST recall."
metadata:
  type: reference
---

Dein Hub hat jetzt einen **Schnellzugriff auf das gesamte Wissen** und eine
**Selbstlern-Schleife**. Drei Werkzeuge in `scripts/recall/`:

| Befehl | Zweck |
|--------|-------|
| `python scripts/recall/recall.py "<frage>"` | Sucht in EINEM Aufruf über alle Speicher (Memory + Wissensbasis + Logs/Historie + Akten), gerankt, mit Pfad + Snippet. Kurz: `recall "<frage>"`. |
| `python scripts/recall/memory_index.py` | Baut `MEMORY.md` als thematischen Register-Index — sammelt verwaiste Merkdateien automatisch ein. |
| `python scripts/recall/journal.py` | Sichert die letzte Übergabe dauerhaft + baut eine durchsuchbare Ereignis-Zeitleiste. |
| `python scripts/recall/feedback.py add "…"` / `review` | Hält Feedback pro Aufgabe fest, wertet Muster aus. |

**Verbindlich:** bei jeder „Stand / was ist mit X / was war wann"-Frage ZUERST `recall`
laufen lassen, dann das genannte Original öffnen (nie raten, immer die Quelle lesen).
Beim Beenden `journal.py` + `memory_index.py` laufen lassen.
