---
name: Responsive Arbeitsweise — Owner muss erreichbar bleiben
description: Lange blockierende Tool-Calls verhindern, dass der User seinen Gedankenfluss einbringen kann. Background-Mode + parallele Calls + Pause-Punkte.
type: feedback
---

**Regel:** Niemals so arbeiten, dass der Owner zwischen Tool-Calls nicht einhaken kann. Wenn er einen Gedanken hat, muss ich erreichbar sein — sonst wird die Zusammenarbeit extrem langsam.

❌ **Anti-Patterns, die ich NICHT mehr mache:**
- `docx2pdf` synchron — pro Konvertierung 13–18s blockiert
- Mehrere lange Bash-Calls hintereinander synchron
- Riesige `Write`/`Edit`-Blöcke (ganze Scripts) ohne Pause-Punkt
- `WebSearch` sequenziell statt parallel (4 Searches × 8s = 32s blockiert)
- `Glob` auf Pfade mit Apostroph ohne Timeout-Fallback
- Iterative Doc-Builds, bei denen ich ungefragt direkt Word **und** PDF baue (= 18s pro Iteration "tot")

✅ **Pflicht-Patterns:**

1. **Background für alles >10s.** `docx2pdf`, große git ops, lange Builds: `run_in_background:true` setzen, Notification abwarten, in der Zwischenzeit antwortbereit sein.

2. **Parallel statt sequenziell.** Unabhängige Tool-Calls IMMER in einer Message bündeln. Read + Glob + Grep + Bash zusammen — nicht hintereinander.

3. **Vor langen Aktionen ankündigen.** Eine Zeile reicht: *"baue jetzt X, ~20s — wenn was reinkommt, schreib einfach"*.

4. **Iterative Doc-Builds: NUR Word, dann fragen.** Bei Memo/Vertrag/PDF-Workflow: erst Word erzeugen, *„ok so?"* fragen, **erst nach Freigabe** PDF konvertieren.

5. **Datei-Suche umfassend.** Bei *"wo ist Datei X"* auch Temp-, Downloads- und Ansicht-/Staging-Ordner mit-greppen. Apostroph-Pfade sofort per PowerShell-Fallback statt erneutem Glob-Versuch.

6. **30s-Stille-Regel.** Spätestens nach 30s einzelnem Tool-Call einen kurzen Status-Ping.

7. **Speak first, act second.** Nach JEDER User-Nachricht ZUERST eine kurze Text-Antwort (Plan/Verständnis), DANN Tool-Calls.

8. **Schritt-für-Schritt statt Block-Salve.** Bei Multi-Aufträgen nicht 4 Tool-Calls auf einmal feuern. Schritt 1 → Status → Schritt 2 → Status. Block-Salven (4+ Calls am Stück) sind verboten.

9. **User arbeitet parallel.** Der Owner macht oft selbst etwas. Bei längeren Aufträgen zwischen Schritten kurz checken: "Punkt X noch dran oder schon erledigt?"

10. **Architektur-Grenze ehrlich benennen.** Während ein Tool-Call läuft, bin ich taub für User-Nachrichten. Funklöcher minimieren durch kurze Calls + Background + Schritt-für-Schritt.

**Why:**
Lange blockierende Tool-Calls verhindern, dass der Owner einhaken und seinen Gedankenfluss in laufende Arbeiten einbringen kann. Das kostet Tempo und Kontrolle.

**How to apply:**
- Bei JEDER Tool-Call-Sequenz: prüfen — parallelisierbar?
- Bei JEDEM Tool-Call >10s: ankündigen ODER background
- Build-Workflows: Iteration auf Word-Ebene, PDF erst final
- Datei-Suche: Temp + Downloads + Ansicht/Staging als Default-Pfade
