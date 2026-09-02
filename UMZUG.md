# UMZUG & NOTFALL — Business-Hub wiederherstellen

**Stand:** 02.09.2026 · **Gilt für:** `business_hub_Dirk_STARTER` auf macOS

Dieses Dokument beantwortet zwei Fragen:

1. **Notfall:** Das MacBook ist weg, gestohlen oder kaputt. Wie arbeite ich morgen weiter?
2. **Umzug:** Neuer Rechner geplant. Was muss mit, in welcher Reihenfolge?

> **Die eine Sache, die du wissen musst:** Der Hub-Ordner ist über GitHub gesichert
> (`x-media-music/business-hub`). Die **Zugangsdaten sind es bewusst nicht** — sie sind
> gitignored. Ohne sie ist der wiederhergestellte Hub eine leere Hülle.
> Siehe **Teil C**.

---

## TEIL A — Notfall: neuer/geliehener Mac, so schnell wie möglich arbeitsfähig

Reihenfolge einhalten. Schritt 1–4 reichen für „ich kann wieder arbeiten".

### 1. Claude Desktop installieren + einloggen
Damit sind sofort wieder da: alle Chats, das Projekt „Business-Hub_Dirk" samt
Projekt-Anweisungen, Claude-Memory, und alle **Web-Connectoren** (Gmail, Google
Calendar, Todoist, Supabase, Canva, Make, Zapier, Brevo). Die hängen am Konto,
nicht am Rechner.

### 2. Hub aus GitHub klonen
```bash
mkdir -p ~/Documents/Claude/Projects
cd ~/Documents/Claude/Projects
git clone https://github.com/x-media-music/business-hub.git business_hub_Dirk_STARTER
```
Der Pfad muss **exakt** so heißen — die launchd-Jobs und einige Scripts enthalten
ihn fest verdrahtet.

### 3. Zugangsdaten einspielen  ← der kritische Schritt
Diese drei Dateien sind **nicht** im Git. Die Werte stehen seit 02.09.2026 in
der Apple-**Passwoerter-App** (8 Eintraege: 6x `strato.de`, 2x `supabase.com`) —
dort nach Titel `Strato:` bzw. `Supabase:` suchen und von Hand eintragen:

| Datei | Inhalt |
|---|---|
| `scripts/mail.env` | Strato IMAP/SMTP — 8 Postfächer inkl. Passwörter |
| `scripts/crm_keys.env` | Supabase URL + Project-Ref + Service-Role-Key (CRM) |
| `scripts/buchhaltung_keys.env` | Supabase-Zugang Buchhaltung |

Als Notlösung ohne Backup: Strato-Passwörter im Strato-Kundenbereich neu setzen,
Supabase-Keys im Supabase-Dashboard neu generieren. Dauert, geht aber.

Sofort testen:
```bash
python3 scripts/check_inbox.py --from rechnung --since 2026-08-01
python3 scripts/audit_hub.py
```

### 4. Ordner in Claude Desktop freigeben
In der Desktop-App den Ordner `business_hub_Dirk_STARTER` als Kontext hinzufügen.
Ordner-Freigaben sind **pro Rechner** und werden nie synchronisiert.

**→ Ab hier ist normales Arbeiten wieder möglich.**

---

### 5. Hintergrund-Jobs wieder einrichten
```bash
open HUB-Jobs-einrichten.command
```
Doppelklick genügt. Richtet ein:

| Zeit | Job | Was |
|---|---|---|
| 06:45 | `com.xmedia.hub.kontakte` | Apple-Adressbuch → `module/kontakte/kontakte.csv` |
| 06:50 | `com.xmedia.hub.ansichtcleanup` | Staging-Ordner aufräumen/archivieren |

Falls „Operation not permitted" erscheint: macOS muss Terminal/python3 in
*Systemeinstellungen → Datenschutz & Sicherheit → Festplattenvollzugriff*
freigegeben werden.

### 6. Lokale MCP-Server neu aufsetzen
Diese liegen **außerhalb** des Hub-Ordners im Benutzerverzeichnis und sind
weder im Git noch (falls Documents-Sync genutzt wird) in iCloud:

| MCP | Ordner auf dem alten Mac | Zweck |
|---|---|---|
| apple-calendar | `~/apple-calendar-mcp` | iCloud-Kalender „Dirk" lesen/schreiben |
| macos-contacts | `~/macos-contacts-mcp` | Kontakte live lesen/anlegen |
| xmedia-crm | (Pfad prüfen) | CRM-Anfragen, Angebote, Verträge |
| pdf-viewer | (Pfad prüfen) | PDFs anzeigen |

Dazu die Konfiguration, welche MCPs geladen werden:
`~/Library/Application Support/Claude/` — ebenfalls nicht synchronisiert.

**Ohne diese Server läuft der Hub trotzdem** — es fehlen nur Kalender-,
Kontakt- und CRM-Direktzugriffe.

### 7. Apple-Daten
Kontakte und Kalender kommen über den iCloud-Login von selbst zurück.
Danach einmal `python3 scripts/kontakte_export.py` laufen lassen, damit der
lokale Cache wieder da ist.

### 8. Das „Dach" nicht vergessen
Die Routing-Datei `~/Documents/Claude/Projects/_dach/CLAUDE.md` und das
technische Gehirn `x-media` liegen **außerhalb dieses Repos**.
→ Prüfen, ob die ebenfalls versioniert/gesichert sind. Wenn nicht: nachholen.

---

## TEIL B — Was wo lebt

| Bestandteil | Ort | Kommt beim Rechnerwechsel automatisch mit? |
|---|---|---|
| Chats, Projekte, Projekt-Anweisungen | Claude-Konto | **ja** (Login genügt) |
| Claude-Memory | Claude-Konto | **ja** |
| Web-Connectoren (Gmail, Todoist, Supabase, Canva, Make, Zapier, Brevo) | Claude-Konto | **ja** |
| Hub-Dateien, Module, Scripts, Regeln, Vorlagen | GitHub-Repo | ja, per `git clone` |
| `.env`-Zugangsdaten | nur lokal | **nein** — separat sichern |
| Lokale MCP-Server + deren Konfig | `~/` und `~/Library/…` | **nein** |
| launchd-Jobs | `~/Library/LaunchAgents` | nein, aber per Command-Datei reproduzierbar |
| Ordner-Freigabe in Claude Desktop | pro Rechner | **nein** |
| `backups/`, `logs/` | nur lokal | nein (Verlust verkraftbar) |

---

## TEIL C — Was NICHT im Git liegt (die echten Lücken)

Bewusst ausgeschlossen über `.gitignore`. Bei einem Totalverlust des Macs ist
das **weg**, wenn es nicht anderswo gesichert ist:

### Kritisch — ohne separates Backup nicht wiederherstellbar

- ~~`scripts/mail.env`, `scripts/crm_keys.env`, `scripts/buchhaltung_keys.env`~~
  → **ERLEDIGT 02.09.2026**: alle 8 Werte liegen in der Apple-Passwoerter-App
  und wurden mit `Zugangsdaten-pruefen.command` zeichengenau gegen die Dateien
  verifiziert. Bei jeder Passwortaenderung dort nachziehen.
- **`module/booking/wohnzimmerkonzerte/`** — interne Kalkulation + Gastgeber-Adressen
  (`.numbers`, `.xlsx`, `.csv`, `_extern_export/`). Vertraulich, deshalb nicht im
  Repo — aber auch **nirgends sonst gesichert**. Braucht einen eigenen,
  verschlüsselten Sicherungsweg.

### Unkritisch — regenerierbar

- `module/kontakte/kontakte.csv` + `mailverkehr.csv` + `vorschlaege_kontakte.csv`
  → per `kontakte_export.py` / `mailverkehr_index.py` neu erzeugbar
- `backups/` (110 MB Zwischenstände), `logs/`, `__pycache__/`, `.DS_Store`

### Sicherungsstand des Repos

Getrackt sind ca. 771 Dateien / 214 MB, inklusive `module/buchhaltung` (224 MB
Belege) und `memory/` — das ist bewusst so und gut. **Aber:** GitHub ist nur so
aktuell wie der letzte Push. Alles, was seither entstanden ist, existiert nur
auf dem Mac.

---

## TEIL D — Weichen, die JETZT gestellt gehören

Damit Teil A im Ernstfall auch wirklich funktioniert:

1. ~~**Die 8 Zugangsdaten in den Passwortmanager**~~ — **ERLEDIGT 02.09.2026.**
   Dafür gibt es einen gefuehrten Helfer im Hub-Root:
   ```
   Doppelklick auf  Zugangsdaten-sichern.command
   ```
   Er legt jeden Wert einzeln in die Zwischenablage, zeigt Titel/Benutzername/
   Website fuer den Eintrag an und leert die Zwischenablage am Ende.
   Nichts wird angezeigt, nichts verlaesst den Mac.

   Danach stehen in der Passwoerter-App:
   - 6x `strato.de` — je ein Eintrag pro Postfach (info@, rechnung@, anfrage@,
     ninox@ bei xmedia24.com; info@, rechnung@ bei xmedia-event.de)
   - 2x `supabase.com` — Service-Role-Key CRM (`vrntqlmrxlbnhetskwjw`)
     und Buchhaltung (`hsvpjtpzsnfdpibdkxut`)

   Im Notfall (Teil A, Schritt 3) werden die Werte von dort per Hand zurueck in
   `mail.env`, `crm_keys.env` und `buchhaltung_keys.env` eingetragen. Die
   Server-/URL-Zeilen dieser Dateien stehen im Repo-Template und im Git.

   **Kontrolle jederzeit:** Doppelklick auf `Zugangsdaten-pruefen.command`.
   Er vergleicht jeden Eintrag der Passwoerter-App zeichengenau mit der Datei
   im Hub und meldet OK oder FEHLER — ohne einen Wert anzuzeigen.
   Nach jeder Passwortaenderung einmal laufen lassen.

2. **Time Machine oder ein gleichwertiges Vollbackup aktivieren.**
   Das ist die einzige Sicherung, die auch `~/Library`, die MCP-Server und die
   Keys mitnimmt. Alles andere hier deckt nur Teilbereiche ab.

3. **Push-Disziplin ernst nehmen.**
   Die Regel steht in `CLAUDE.md` (`git pull` vor, `git commit`+`git push` nach
   der Arbeit) — sie wird aber nicht immer eingehalten. Faustregel: **kein
   Feierabend mit uncommitteten Änderungen.**
   ```bash
   git status --short          # was ist offen?
   git add -A && git commit -m "Hub-Stand TT.MM.JJJJ" && git push
   ```

4. **`wohnzimmerkonzerte/` gesondert sichern.**
   Verschlüsselter Ordner oder Passwortmanager-Anhang — nicht auf GitHub.

5. **`_dach/` und `x-media` prüfen.**
   Liegen außerhalb dieses Repos. Wenn sie nicht versioniert sind, ist die
   Routing-Logik des gesamten Setups ungesichert.

6. **Zwei Macs gleichzeitig: nur mit Git, nicht mit Cloud-Sync.**
   `aufgaben.csv`, `memory/` und die Logs vertragen kein paralleles Schreiben
   über iCloud/Dropbox — das erzeugt Konfliktkopien statt Merges. Ein führender
   Rechner, oder konsequent über `git pull` / `git push` arbeiten.

---

## Kurzfassung für den Ernstfall

```
1. Claude Desktop installieren + einloggen
2. git clone …/business-hub.git → ~/Documents/Claude/Projects/business_hub_Dirk_STARTER
3. mail.env + crm_keys.env + buchhaltung_keys.env aus dem Passwortmanager einspielen
4. Ordner in Claude Desktop freigeben
→ arbeitsfähig. Rest (Jobs, MCPs) in Ruhe nachziehen.
```
