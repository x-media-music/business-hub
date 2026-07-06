---
name: Ansicht-Cleanup nur nach Original-Verifikation
description: Beim Aufräumen des Ansicht-/Staging-Ordners vor jeder Verschiebung verifizieren, dass die Original-Datei am korrekten Produktivplatz liegt. Wenn kein Original gefunden — NICHT verschieben, dem Owner melden.
type: feedback
---
Vor jedem Aufräumen des Ansichts-/Staging-Verzeichnisses muss für **jede** Datei, die ins `_archiv` verschoben werden soll, **vorher** verifiziert werden, dass das Original am richtigen Produktivplatz tatsächlich existiert.

**Why:** Leitsatz „nichts darf verloren gehen" (vgl. `feedback_ende_befehl.md`). Der Ansicht-Ordner ist nur Staging — Originale sollen am richtigen Produktivplatz liegen. Wenn ein „Original" nicht auffindbar ist, könnte die Ansicht-Kopie de facto die einzige Version sein — Verschieben würde dann Verlust riskieren.

**How to apply:**
- Vor jedem Cleanup-Lauf:
  1. Liste der Kandidaten zusammenstellen (alle Dateien älter als 7 Tage, plus heute obsolete Dateien — z.B. Entwurf durch Final ersetzt, alte PDF-Version durch neue).
  2. Für jeden Kandidaten den erwarteten Original-Pfad bestimmen und mit `Path.exists()` verifizieren.
  3. Nur Dateien mit verifiziertem Original verschieben.
  4. „Original nicht gefunden"-Dateien dem Owner berichten — nicht eigenmächtig verschieben/löschen.
- Verschoben wird ins `_archiv`-Subfolder. Konvention: Datei behält den Namen, wenn sie schon ein Datum im Namen trägt; sonst `YYYY-MM-DD_`-Prefix.
- Unklare Fälle bleiben im Ansicht-Ordner zur weiteren Klärung.
