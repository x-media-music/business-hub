# CRM-Datenbank-Zugang (Supabase)
**Typ:** Thema / Zugang
**Zuletzt_gesynct:** 2026-07-02

## Das Wichtigste
- Das x-media CRM (React-App auf Hostinger) hängt an **Supabase** (Postgres). Ich kann es
  direkt **lesen und steuern** — über die Supabase-MCP-Tools (SQL) und über die Storage-/REST-API.
- **Projekt-Ref:** `vrntqlmrxlbnhetskwjw` · **URL:** `https://vrntqlmrxlbnhetskwjw.supabase.co`
- **Zugangsdaten (lokal, gitignored):** `scripts/crm_keys.env`
  - `SUPABASE_SERVICE_ROLE_KEY` — hebelt RLS aus, **nie ins Frontend/GitHub**. Nur serverseitig/CLI.
  - Herkunft: Supabase-Dashboard → Project Settings → API Keys → Tab „Legacy anon, service_role".
- Damit muss ich künftig **nicht mehr nach Zugängen fragen** (Wunsch Dirk, 02.07.2026).
- **Nicht** die Dropbox anfassen — CRM-Keys leben ab jetzt hier im Hub-Projekt.

## Wichtige Eigenheiten
- Das CRM-**Frontend** nutzt für Löschen ein natives `confirm()`-Fenster. Das friert die
  Browser-Steuerung ein (lässt sich von außen nicht wegklicken). → Löschen/Schreiben besser
  **direkt über DB (SQL) oder Storage-API**, nicht über den UI-Button.
- **Storage:** Direktes Löschen aus `storage.objects` per SQL ist per Trigger blockiert
  („protect_delete"). → Storage-Dateien über die **Storage-API** löschen:
  `curl -X DELETE "$SUPABASE_URL/storage/v1/object/<bucket>/<pfad>" -H "apikey: $KEY" -H "Authorization: Bearer $KEY"`
- Angebots-PDFs liegen in zwei Buckets: `crm-app` (`angebote/<Nr>.pdf`) und
  `angebote-pdfs` (`<angebot_id>/Angebot_<Nr>.pdf`).

## Kern-Tabellen (FK-Kette bei Löschung beachten)
- `anfragen` (Pipeline) ← `angebote`, `kalender`, `kontaktverlauf_crm` referenzieren `anfrage_id`.
- Reihenfolge beim Löschen eines Vorgangs: kalender → kontaktverlauf_crm → angebote → anfragen.
- Veranstalter (`veranstalter`) NICHT mitlöschen (eigener Stammdatensatz).

## Verlauf
| Datum | Wer | Was |
|---|---|---|
| 2026-06-30 | Dirk | Test-Angebot „Testevent 2027" (XE-2026-021) angelegt |
| 2026-07-02 | Hub | Testvorgang komplett gelöscht (angebot 618, anfrage 632, kalender 337, kontaktverlauf 117 + 2 Storage-PDFs). Backup: `backups/2026-07-02_loeschung_testevent-2027_XE-2026-021.json` |
| 2026-07-02 | Dirk | Service-Role-Key bereitgestellt → in `scripts/crm_keys.env` hinterlegt (autonomer CRM-Zugang) |
