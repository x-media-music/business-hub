---
description: Vollständige System-Check-Runde deines Hubs (Soll-vs-Ist-Tiefencheck, autonom, 2+ Runden, reine Systemrunde)
---

# /systemcheck — Reine System-Check-Runde

**Wenn dieser Befehl abgerufen wird, ist dieser Chat eine REINE SYSTEMRUNDE. Es gibt KEIN Tagesgeschäft.** Kommt trotzdem eine Tagesgeschäft-Anfrage, freundlich abweisen: *„Dieser Chat ist eine Systemrunde — Tagesgeschäft im nächsten Chat."* Nicht bearbeiten.

Ziel: **schneller · besser · zuverlässiger.** Der Hub wird gegen sein eigenes Regelwerk geprüft, Lücken/Drift/tote Verdrahtung gefunden, sicher gefixt, gegengetestet — und zwar **immer gegen die AKTUELLE Version** des Hubs, nie gegen eine eingefrorene Checkliste.

---

## Grundprinzipien (nicht verhandelbar)

1. **Immer aktuell, nie verrottend.** Jeder Lauf liest die aktuellen `CLAUDE.md` + `.claude/rules/*.md` + Scripts + geplante Tasks/Hooks + Memories **frisch** ein und prüft gegen den echten Ist-Stand. Der deterministische Harness (`scripts/audit_hub.py`) leitet tote Verweise **aus den aktuellen Regeln + dem Dateisystem** ab — er darf nicht zu einer statischen Liste degenerieren. Findet ein Lauf eine neue Verdrahtung, die der Harness noch nicht kennt, wird der Harness im selben Lauf erweitert.
2. **Autonom.** Innerhalb der Runde wird NICHT nachgefragt — Fixes werden selbst gesetzt UND getestet. Einzige Ausnahme: echte Blocker (etwas, das nur der Owner tun kann — z.B. eine Aktion nach außen, eine Zahlung, eine Zugangs-/Secret-Rotation). Solche Blocker werden nicht gerusht, sondern sauber als „braucht deine Aktion" in den Bericht gelegt.
3. **Faktenbasis, kein Raten.** Jede Empfehlung selbst gegen den echten Code validieren, bevor gefixt wird. Fehlt Wissen → erst die Quelle lesen. Nie eine überholte Memory/Regel „zurückholen".
4. **Verlustsicher.** Nichts geht verloren; Findings festhalten.

---

## Ablauf

### Vorlauf
- Aktuelles Datum/Uhrzeit ziehen. Deklarieren, dass dies eine Systemrunde ist (kein Tagesgeschäft).
- Ist-Inventar: geplante Tasks (Betriebssystem-Scheduler), `.claude/settings.json` (Hooks), Scripts, Module, Memory-Ordner. Falls eine Blaupause `SYSTEM_INDEX.md` existiert, lesen.

### RUNDE 1 — Audit + Analyse + Fix
1. **Harness:** `python scripts/audit_hub.py` (py_compile aller Dateien, Hook-Ziele, JSON-State, Memory-Index-Konsistenz, tote Script- + Memory-Referenzen). Ergebnis festhalten.
2. **Agentische Domänen-Prüfer parallel** (read-only, Beleg mit Datei:Zeile, CONFIRMED vs SUSPECTED): Soll (Regeln/Memories) vs Ist (Scripts/Daten) — tote Verweise, Rule↔Script-Mismatch, Flow-Lücken (Verlust-Risiko), verwaiste Dateien, Kontrollfluss-Bugs. Prüfbereiche aus den tatsächlich vorhandenen Regel-Dateien ableiten (nicht aus einer festen Liste).
3. **Aggregieren + selbst verifizieren.** Jede kritische Finding gegen echten Code prüfen (Agenten können irren). Findings festhalten.
4. **Sicher fixen mit Test.** Klare Verdrahtungs-Bugs/Lücken beheben, jeweils `py_compile` + gezielter Test. Risiko-/Ermessens-/„braucht-Owner"-Punkte NICHT eigenmächtig — in den Bericht.

### RUNDE 2 — identische Wiederholung (Regression)
- `audit_hub.py` erneut + betroffene Bereiche neu prüfen. **Ziel: 0 FAIL, keine neu eingeschleppten Fehler.**
- Wurde in Runde 2 **erneut etwas gefixt → RUNDE 3** (gleiche Wiederholung).
- Droht eine **4. Runde:** Chat-Volumen bewerten. Reicht es → weiter. Reicht es nicht → **sauberes ENDE + Empfehlung: `/systemcheck` im nächsten Chat neu starten** (läuft dann gegen den dann-aktuellen Stand).

### Abschluss (wenn eine Runde sauber durchläuft, ohne neue Fixes)
1. **Bericht** (klar strukturiert): Verdikt, behoben & getestet, „war kein Mangel", „braucht deine Aktion", nächste Schritte.
2. **Verifiziertes ENDE:** normale Ende-Prozedur deines Hubs (Übergabe schreiben, MEMORY.md/Index frisch: `python scripts/recall/memory_index.py`, Ereignis-Journal: `python scripts/recall/journal.py`). Dann Empfehlung: **neuen Chat starten, Tagesgeschäft wieder aufnehmen.**

---

## Merke
- Reihenfolge-Governance und Volumen-Check sind Teil des Befehls — lieber sauber im nächsten Chat weiter als eine Runde am Volumen-Limit verhunzen.
- Der Harness ist read-only; er ändert nichts. Fixes machst du bewusst und einzeln, mit Test.
