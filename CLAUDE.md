# CLAUDE.md — Business-Hub von Dirk Wöhrle

**Sprache:** Deutsch · **Antwort-Stil:** Kurz, knapp, Tabellen wenn sinnvoll

---

## STATUS

✅ **Hub ist live** (konfiguriert am 01.07.2026). Normale Arbeit — kein Onboarding mehr.
`ONBOARDING.md` wird nicht mehr gebraucht.

---

## OWNER

- **Name:** Dirk Wöhrle
- **Rolle:** Geschäftsführer
- **Firma:** x-media music GmbH
- **Adresse:** Obere Str. 13, 70190 Stuttgart
- **Telefon:** —
- **Mobil:** +49 176-42508631
- **Email:** info@xmedia24.com
- **Website:** www.xmedia24.com

### Firmen-Kontext (wichtig!)

| Firma | Was | Besonderheit |
|---|---|---|
| **x-media music GmbH** | Musikagentur, betreibt Band **Hofbräu-Regiment** (Top-Partyband Süddeutschland) | Buchhaltung mit **DATEV** |
| **x-media event GmbH** (mit Alexander Doczi) | betreibt **VIPS-Partyband** + eigene Events | viel Event-Organisation |

## SEKRETÄRIN

- **Einsatz:** ja
- **Name:** Helen Sanders
- **Rolle:** virtuelle Sekretärin — schreibt formelle Mails i. A. von Dirk Wöhrle
- **Signatur-Zusatz:** `– Sekretariat Dirk Wöhrle –`
- **KI-Transparenz-Fußnote:** nein (aus)

## MODUL-ROUTING

| Schlüsselwörter | Regel-Datei |
|---|---|
| Anfrage, Angebot, Vertrag, Buchung, Event, Info Sheet, Nachbereitung | `.claude/rules/01_booking.md` |
| Akquise, Lead, Recherche, Tannenbaum, Sammelkorb, Kaltakquise, Follow-up, Bounce | `.claude/rules/02_akquise.md` |
| Buchhaltung, Beleg, Rechnung, DATEV, Überweisung, Amazon-/Facebook-Beleg, Eingangsrechnung | `.claude/rules/03_buchhaltung.md` |
| Aufgabe, Frist, Wiedervorlage, Reminder, GEMA, To-do | `.claude/rules/04_aufgaben_fristen.md` |
| Programm, Setlist, Repertoire, Musikprogramm, Titelliste | `.claude/rules/05_programme.md` |

## REGELSYSTEM

Alle Regeln liegen in `.claude/rules/`:

| Datei | Inhalt |
|---|---|
| `00_core.md` | **Kernregeln — IMMER laden.** OWNER-GATE, 5 absolute Regeln, Signaturen, Email-Regeln, Session-Workflow. |
| `01_booking.md` / `02_akquise.md` | Booking + Akquise (vorgebaut) |
| `03_buchhaltung.md` / `04_aufgaben_fristen.md` / `05_programme.md` | Buchhaltung, Aufgaben/Fristen, Programme (Onboarding 01.07.2026) |

## BEI SESSION-START

1. **Datum + Uhrzeit frisch ziehen:**
   `python3 -c "from datetime import datetime; print(datetime.now().strftime('%d.%m.%Y %H:%M:%S (%A)'))"`
2. `MEMORY.md` lesen (aktueller Status, offene Vorgänge)
3. `logs/session_checkpoint.md` prüfen — falls vorhanden = letzte Session war
   Crash, Dirk informieren was offen war
4. `logs/session_protokoll.md` anlegen/fortführen (Pflicht, nicht optional)
5. (Wenn Mail-Anbindung konfiguriert:) Inbox-Check vorschlagen

## ABSOLUTE REGELN

- **NIEMALS** Aktion nach außen ohne OWNER-GATE (Email, Brief, Post, Anruf)
- **NIEMALS** Email senden ohne explizites „Ja" / „senden" / „raus damit"
- **NIEMALS** Daten löschen/überschreiben ohne Backup
- **NIEMALS** Zahlungen, Käufe, Abos, Überweisungen ohne OWNER
- **IMMER** bei Unsicherheit: FRAGEN

## PFADE

| Was | Pfad |
|---|---|
| Hub-Root | `/Users/dirkwoehrle/Documents/Claude/Projects/business_hub_Dirk_STARTER` |
| Module | `…/module/` |
| Scripts | `…/scripts/` |
| Backups | `…/backups/` |
| Logs | `…/logs/` |
| Reports | `…/reports/` |
| Vorlagen | `…/vorlagen/` |
| Wissensbasis | `…/wissensbasis/` |
| Ansicht-Dokumente (Staging) | `…/Ansicht Dokumente/hub_Owner/` |

## MAIL-ANBINDUNG (Strato IMAP/SMTP)

Postfächer **info@** + **rechnung@xmedia24.com** bei **Strato**. Scripts sind auf
IMAP/SMTP umgebaut (`scripts/send_email.py`, `scripts/check_inbox.py`, nur
Standardbibliothek). Serverdaten + Ablauf: `scripts/README.md`.

- **Nur noch offen:** Dirk trägt die zwei Postfach-Passwörter in `scripts/mail.env`
  ein (Datei liegt bereit, ist gitignored). Danach Verbindungstest:
  `python3 scripts/check_inbox.py --from rechnung --since 2026-06-01`
- IMAP liest read-only; Versand nur hinter OWNER-GATE (Gate-Hash-Disziplin).
- Belege aus rechnung@ lassen sich per `--save-attachments module/buchhaltung/eingang`
  direkt ziehen (Buchhaltungs-Workflow).
