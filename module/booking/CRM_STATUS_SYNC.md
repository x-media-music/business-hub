# CRM-Status mitziehen — fester Workflow-Schritt (seit 13.08.2026)

**Zweck:** CRM und Hub synchron halten. Bei JEDER Status-Änderung eines Booking-Vorgangs
wird der Anfrage-Status im CRM sofort mitgesetzt — kein Vorgang bleibt verwaist.

Anlass: Absage Hofmeier/Löffingen (XM-2026-035). Dirk hat im CRM manuell auf „Verloren"
gesetzt und gewünscht, dass der Hub das künftig automatisch mitmacht (nach kurzer Bestätigung).

## Ablauf
1. Anfrage finden: `mcp__xmedia-crm__lies_anfragen` (Freitext-Suche z. B. Name/Ort/Band).
2. Status setzen: `mcp__xmedia-crm__aktualisiere_anfrage_status`
   - Schutz: ohne `bestaetigt=true` nur Vorschau; erst zweiter Aufruf mit `bestaetigt=true` schreibt.
   - Vor dem Schreiben **kurze Bestätigung von Dirk** (CRM-Schreibvorgang = OWNER-GATE-nah).
3. Im Abschlussbericht vermerken (z. B. „CRM-Status → Verloren").

## Status-Mapping (exakte DB-Schreibweise)
| Hub-Ereignis | CRM-Status |
|---|---|
| Kunde sagt ab / Vorgang verloren | `Verloren` |
| Angebot raus | `Angebot versandt` |
| 1× / 2× nachgehakt | `Angebot versandt 1x nachgehakt` / `Angebot versandt 2x nachgehakt` |
| Mündliche Zusage | `Zusage mündlich` |
| Vertrag versandt | `Vertrag versandt` |
| Fix bestätigt | `Fix` |
| GEMA gemeldet | `GEMA gemeldet` |
| Storno / Archiv | `Storno` / `Archiv` |
| (weiter) | `NEU`, `Rückfrage` |

> **Erledigt am 25.08.2026:** Der Block steht jetzt in `.claude/rules/01_booking.md`
> unter GRUNDPRINZIP und gilt damit für jede Booking-Sitzung. Diese Datei bleibt als
> Langfassung und Herkunftsnachweis bestehen — Änderungen bitte an **beiden** Stellen.
