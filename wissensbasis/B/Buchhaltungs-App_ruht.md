# Buchhaltungs-App / KI-Buchhaltungsassistent (RUHT)
**Typ:** Thema / internes Projekt (stillgelegt)
**Zuletzt_gesynct:** 2026-07-17 08:00

## Das Wichtigste
- **Status: RUHT.** Versuch einer Buchhaltungs-Automatisierung (eigenständige React-PWA + Supabase,
  PDF-Klassifizierung → DATEV-Uploadmail bei music / Dropbox bei event).
  **Dirk kam damit nicht gut klar → Projekt bewusst stillgelegt.** Kein Defekt, kein Handlungsbedarf.
- **`buchhaltung.xmedia24.com` ist offline** (kein DNS-Eintrag / NXDOMAIN) — **so gewollt**.
  Taucht in Hostinger-Warnmails als „betroffene Website" auf → **ignorieren**, nicht „reparieren".
- **Nameserver-Thema:** ebenfalls erledigt — es wird **nichts umgestellt** (internes, stillgelegtes Projekt).
- **Der laufende Beleg-Workflow ist davon NICHT betroffen** — die tägliche Buchhaltung läuft über den Hub
  (`.claude/rules/03_buchhaltung.md`, `scripts/`, Beleg-Check-Task) und lebt unabhängig weiter.

## ⚠️ Befund 17.07.2026 — Zugänge laufen ins Leere
Dirks Annahme war, das Projekt sei „zum Prüfen von Informationen und Zugängen noch zu gebrauchen".
**Geprüft — das stimmt so nicht mehr:**

| Prüfung | Ergebnis |
|---|---|
| `hsvpjtpzsnfdpibdkxut.supabase.co` (Buchhaltungs-Backend) | **löst nicht auf** (NXDOMAIN, HTTP 000) |
| CRM-Supabase (anderes Projekt, Gegenprobe) | antwortet → kein Netzproblem |
| `supabase.com` (Gegenprobe) | HTTP 200 → kein Netzproblem |

→ Das Supabase-Projekt ist **vermutlich gelöscht** (pausierte Projekte lösen normalerweise weiter auf).
Damit sind die Keys in `scripts/buchhaltung_keys.env` (SUPABASE_URL / PROJECT_REF / SERVICE_ROLE_KEY)
**wahrscheinlich tot** — und die Tabellen `bh_belege` / `bh_regeln` / `bh_protokoll` samt Inhalt weg.

**RÜCKFRAGE an Dirk (offen):** Im Supabase-Dashboard nachsehen, ob das Projekt gelöscht oder nur pausiert ist.
- Gelöscht → `scripts/buchhaltung_keys.env` ist Altlast (aufräumen), Daten sind weg.
- Pausiert/reaktivierbar → dann sind die Zugänge doch noch brauchbar.

## Wo liegt was (Wegweiser)
| Was | Wo |
|---|---|
| Vollständiges Projekt-Konzept + Technik (Tabellen, Routing-Logik, DATEV-Adressen) | Skill `buchhaltungsassistent` (SKILL.md) — **bleibt als Wissen erhalten**, auch wenn die App ruht |
| Supabase-Zugänge (Status s. o. — vermutlich tot) | `scripts/buchhaltung_keys.env` (gitignored, nie committen — service_role-Key) |
| **Produktiver** Beleg-Weg (läuft!) | `.claude/rules/03_buchhaltung.md` + `module/buchhaltung/` |

## Verlauf
| Datum | Wer | Was |
|---|---|---|
| 2026-07-02 | Dirk | Supabase-Zugang für Buchhaltungsassistent angelegt (`buchhaltung_keys.env`) |
| 2026-07-15 | Hostinger | Server-Umzug (neue IP 82.198.226.80), listet `buchhaltung.xmedia24.com` als betroffen |
| 2026-07-17 | Claude | Im Morgen-Briefing als NXDOMAIN aufgefallen → als Defekt gemeldet |
| 2026-07-17 | Dirk | Klarstellung: Projekt ruht bewusst, Subdomain muss nicht live sein; NS nicht umstellen |
| 2026-07-17 | Claude | Nachgeprüft: auch das Supabase-Backend löst nicht mehr auf → Zugänge vermutlich tot; Task geschlossen, Rückfrage offen |
