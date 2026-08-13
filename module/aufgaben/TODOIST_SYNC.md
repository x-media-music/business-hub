# Todoist-Sync „Hub Aufgaben"

**Eingerichtet:** 15.07.2026 · **Todoist-Projekt:** „Hub Aufgaben" (ID `6h5pJ7fgQrJqM9C4`, orange, Favorit)

## Prinzip
- `module/aufgaben/aufgaben.csv` bleibt die **Quelle der Wahrheit** (volle Notizen/Historie).
- Jede OFFENE Aufgabe wird nach Todoist gespiegelt; die Todoist-ID steht am Zeilenende als `[TD:<id>]`.
- **Dirk hakt in Todoist ab** (App/Handy). Das Morgen-Briefing synct täglich.

## Sync-Regeln (für Morgen-Briefing / jede Session)
1. **Todoist → CSV:** Für jede CSV-Zeile mit `[TD:id]` und Status OFFEN prüfen, ob die Todoist-Task erledigt ist (find-completed-tasks im Projekt 6h5pJ7fgQrJqM9C4 bzw. fetch-object). Erledigt → CSV-Status ERLEDIGT + Vermerk `[TD-abgehakt <Datum>]`. Vorher CSV-Backup.
2. **CSV → Todoist:** Neue OFFENE Aufgabe ohne `[TD:]` → per add-tasks ins Projekt spiegeln (content=Titel, description=Kategorie/Bezug/Notiz-Kurzfassung, dueString=Fälligdatum, label=Kategorie, p1=überfällig/heute, p2=≤7 Tage, sonst p4) und `[TD:id]` in die CSV schreiben.
3. Wird eine Aufgabe im Hub geschlossen (ERLEDIGT/DUBLETTE), die Todoist-Task per complete-tasks abhaken.
4. Fälligkeits-Änderungen im Hub → reschedule-tasks (NICHT update-tasks).
5. Todoist-Projekt „Für Claude" (6h33QX2Rp3VQCM6j) bleibt separat = Dirks Zurufe an Claude.

## Wichtig
- Abhaken in Todoist ist **kein** OWNER-GATE-Ersatz: Es schließt nur die Aufgabe. Mails/Zahlungen brauchen weiterhin explizite Freigabe.

## Kommentare = Arbeitsaufträge (ergänzt 15.07.2026)
Dirk kommentiert Aufgaben in „Hub Aufgaben" mit Anweisungen. Bei jedem Sync:
1. Neue Kommentare holen: find-activity (objectType=comment, eventType=added, projectId 6h5pJ7fgQrJqM9C4), seit letztem Lauf; eigene (von Claude gepostete) Kommentare ignorieren — nur die neuesten seit last_run beachten, bereits beantwortete nicht doppelt abarbeiten (erkennbar an Claude-Antwortkommentar danach).
2. Als Arbeitsauftrag behandeln: erst QUERPRÜFEN (verarbeitet.csv, Wissensbasis, Mail-Verlauf — evtl. längst erledigt!), dann ausführen/vorbereiten. Außenwirkung (Mail, DATEV, Zahlung) weiterhin NUR über OWNER-GATE.
3. Ergebnis als Antwort-Kommentar an die Task hängen (add-comments): was getan/vorbereitet, wo es liegt, was noch von Dirk gebraucht wird.
