---
name: Session-Start Pflichtprogramm bei jedem "hi"
description: Bei "hi"/"hallo"/"moin"/"guten morgen" sofort volles Pflichtprogramm — kein lapidarer Einzeiler.
type: feedback
---
**Regel:** Sobald der Owner eine Session mit *jeglicher* Begrüßung eröffnet ("hi", "hallo", "moin", "guten morgen", "tag", "servus", "na", "👋" o.ä. — auch ohne weiteren Auftrag), muss SOFORT das komplette Session-Start-Pflichtprogramm laufen. Kein Smalltalk, kein "Was steht an?"-Einzeiler.

**Pflichtprogramm (Reihenfolge wie in `00_core.md` „BEI SESSION-START PRÜFEN"):**

0. Datum/Uhrzeit/Wochentag frisch ziehen (`python -c "from datetime import datetime; print(...)"`) — nie raten
1. Projektlokale `MEMORY.md` lesen
2. Etwaige Fehler-/Nachbearbeitungs-Marker prüfen
3. `logs/session_checkpoint.md` prüfen — falls vorhanden = Crash, Owner informieren
4. **Diskretions-Check FRAGEN** ([Ja/Nein/Später]) — VOR allen Zahlen/Umsätzen/Kontoständen!

**Sobald der Diskretions-Check beantwortet ist (egal ob Ja/Nein/Später) — automatisch direkt anschließend:**

5. **Offene Aufgaben/Tasks** ziehen — überfällige markieren, hohe Priorität hervorheben
6. **Kalender** für heute + kommende Tage — mit relevanten Kategorien
7. **Konsolidiertes Briefing als Tabellen-Block** — abgeleitet aus MEMORY + Tasks + Kalender:
    - 🔥 Heute fällig
    - ⚠️ Überfällig
    - 📅 Diese Woche / Nächste Tage
    - 📋 Mittelfristig (PRIO-Punkte aus MEMORY)
    - Bei Diskretion=Nein/Später: Zahlen/Beträge/Kontostände rausnehmen, Sachthema bleibt

8. **Ansicht-Cleanup (stille Wartung)** — `python3 scripts/ansicht_dokumente_cleanup.py` ausführen
   (räumt `Ansicht Dokumente/hub_Owner/` verlustsicher auf: >7 Tage mit produktivem Original → `_archiv`;
   im Cloud-Lauf werden Dateien nur verschoben, nativ auch alte Archiv-Kopien gelöscht). Ersetzt den
   früheren launchd-Job. **Nicht breittreten** — nur wenn `reports/ansicht_cleanup_report.md`
   Einzelkopien listet, diese im Briefing knapp als „produktiv ablegen" melden.

**Was NICHT automatisch läuft:**
- Inbox-Check — bleibt sprach-getriggert („checke emails", „lese emails", „was kam rein"). Grund: der Cursor-Modus soll bewusst beim ersten echten Email-Befehl losgehen, sonst rückt er bei jeder Session-Eröffnung weiter und Mails wirken „schon gelesen".

Erst dann auf die Folgenachricht des Owners warten.

**Why:** Ein lapidarer Einzeiler bei „hi" zwingt den Owner, das Anschieben selbst zu übernehmen, und Pflicht-Checks (MEMORY, Marker, Diskretions-Check, Briefing) werden übersprungen. Das volle Pflichtprogramm stellt sicher, dass der Owner sofort einen sauberen Stand hat.

**How to apply:**
- Auch bei einsilbiger Begrüßung: vollständig durchziehen, nicht abkürzen
- Ein etwaiger Session-Check-Hook-Output ersetzt das Pflichtprogramm NICHT — er ist nur eine Status-Schnellanzeige
- Wenn der Owner zusätzlich eine Aufgabe in der Begrüßung mitliefert („hi, was wurde aus X?"), erst Pflichtprogramm + Diskretions-Check, dann auf X eingehen
- Bei sehr knapper Begrüßung darf der Briefing-Block kompakt sein, aber NIE fehlen — Tabelle reicht
- Diskretions-Status neu erfragen (gilt sessionweise, nicht über Sessions hinweg)
