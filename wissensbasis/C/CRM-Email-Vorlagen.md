# CRM-E-Mail-Vorlagen (`email_templates`)

**Typ:** Thema
**Zuletzt_gesynct:** 2026-08-17 19:20

## Das Wichtigste

Alle Vorlagen für den CRM-Versand (Angebot, Nachfassen, Vertrag, GEMA, Absage) liegen in
Supabase `vrntqlmrxlbnhetskwjw` (x-media CRM), Tabelle **`email_templates`**.
Versand über MCP `xmedia-crm` → `versende_angebot` (Parameter `template_key`).
**Ohne `bestaetigt=true` ist jeder Aufruf reine Vorschau** — ideal zum Testen von Vorlagen.

## ⚠️ Platzhalter — zwei Syntaxen, nicht verwechseln

| Doppelklammer `{{…}}` — Personen-/Vorgangsdaten | Einfache Klammer `{…}` — Stammdaten |
|---|---|
| `{{anrede}}` (Frau/Herr), `{{vorname}}`, `{{nachname}}`, `{{angebots_nr}}`, `{{reserviert_bis}}` | `{bandname}`, `{veranstaltung}`, `{datum}`, `{ort}`, `{bandleader}`, `{reservierung_bis}` |

**`{vorname}` mit einfachen Klammern wird NICHT ersetzt** und geht roh an den Kunden raus.
Das war der Bug in `buchungsbestaetigung` (gefunden + behoben 17.08.2026).
Im **Betreff** funktionieren die einfachen Klammern; `{{angebots_nr}}` funktioniert dort ebenfalls.

## ⚠️ Anrede + Grußformel setzt teilweise der Webhook

**Entscheidend: Der Webhook setzt eine Anrede NUR, wenn die Vorlage selbst keine hat —
und nur bei Plain-Text-Vorlagen.** Seine Anrede ist die bessere: grammatisch korrekt
(„Sehr geehrte **Frau** Valzano," / „Sehr geehrter **Herr** …"), was eine Vorlage mit
`{{anrede}}` nicht hinbekommt („Sehr geehrte/r Frau Valzano,").

| Vorlagentyp | Anrede | Schluss |
|---|---|---|
| Plain-Text, **DU** | Webhook setzt „Hallo <Vorname>," → **NICHT in die Vorlage schreiben** | Webhook hängt „Beste Grüße" + HTML-Signatur an |
| Plain-Text, **SIE** | Webhook setzt „Sehr geehrte/r <Anrede> <Nachname>," korrekt gebeugt → **NICHT in die Vorlage schreiben** | Webhook hängt „Mit freundlichen Grüßen" + HTML-Signatur an |
| HTML (`<p>…`) | Webhook setzt **keine** → Anrede **muss** in die Vorlage | Webhook hängt nur die HTML-Signatur an |

**Regel:** Plain-Text-Vorlage → ohne Anrede beginnen. HTML-Vorlage → eigene Anrede nötig;
dort `Guten Tag {{anrede}} {{nachname}},` verwenden, weil das für beide Geschlechter
grammatisch aufgeht.

**Konsequenz:** Steht in der Vorlage ein eigener Schlussblock („Mit freundlichem Gruß / x-media
music GmbH / Dirk Wöhrle"), erscheint die Grußformel **dreifach**. Schlussblock gehört NICHT
in die Vorlage.

`zusatz_text` wird **ans Ende des Vorlagentexts** gehängt, direkt vor die Grußformel.

## Reparaturen 17.08.2026

| id | Vorlage | War kaputt | Behoben |
|---|---|---|---|
| 5 | `buchungsbestaetigung` | `{vorname}` roh im Text · dreifache Grußformel | Anredezeilen + Schlussblock raus, SIE auf `{{anrede}} {{nachname}}` |
| 2 | `nachfassen_1` | Betreff `{{bandname} – {veranstaltung}}` → Klammern im Betreff sichtbar · verwaistes `</strong>` · „einen Angebot" | Betreff auf einfache Klammern, HTML + Grammatik bereinigt, Angebotsnr. ergänzt |
| 3 | `nachfassen_2` | Textfragment `<p>. <strong>{{angebots_nr}}</strong>.</p>` · Widerspruch Betreff („endet bald") ↔ Text („ist abgelaufen") | Fragment integriert, Text auf „Reservierung ausgelaufen" vereinheitlicht |
| 9 | `vertrag_nach_unterschrift` | Anrede komplett leer („Sehr geehrte/r ," / „Lieber ") · Betreff leer · doppelte Grußformel | Platzhalter-Anrede (SIE) bzw. Anrede entfernt (DU), Betreff gesetzt, Schlussblock raus |

| 6 | `GEMA` | Betreff leer · doppelte Grußformel · Tippfehler „DEine" | Betreff gesetzt, Schlussblock raus, Tippfehler korrigiert |
| 10 | `nachfassen_vertrag` | Betreff „Vertrag- {bandname}" (fehlendes Leerzeichen, ohne Datum) | Betreff auf „Vertrag – {bandname} – {veranstaltung} am {datum}" |

Originale gesichert: `backups/crm_email_template_5_buchungsbestaetigung_20260817.md` ·
`backups/crm_email_templates_2_3_9_20260817.md` · `backups/crm_email_templates_1_6_10_20260817.md`

**Alle acht Vorlagen wurden nach der Reparatur in beiden Anredeformen per Vorschau gegengelesen.**
`angebot_versand` (1) war in Ordnung und blieb unverändert.

## Entscheidungen

- **„Guten Tag {{anrede}} {{nachname}}," bleibt vorerst so** (Dirk, 17.08.2026) — betrifft die
  HTML-Vorlagen `nachfassen_1` + `nachfassen_2`. Falls später doch „Sehr geehrte…" gewünscht:
  entweder geschlechtsabhängige Anrede im n8n-Workflow, oder die zwei Vorlagen auf Plain-Text
  umstellen, dann setzt der Webhook die korrekt gebeugte Anrede automatisch.

## Verlauf

| Datum | Wer | Was |
|---|---|---|
| 17.08.2026 | Hub | Bug `{vorname}` beim Vertragsversand an K. Valzano entdeckt, Vorlagen 5/2/3/9 repariert, Platzhalter-Logik dokumentiert |
