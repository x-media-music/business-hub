# Memory Index — Dirk Wöhrles Business-Hub

Persistenter Speicher. Details in den verlinkten Dateien.
Format pro Eintrag: `- [Titel](datei.md) — einzeilige Kurzbeschreibung`

**Hub konfiguriert:** 01.07.2026 · **Owner:** Dirk Wöhrle

## ⭐ NORDSTERN

- **Super-Gehirn-Standard:** treffsicher, proaktiv, Stand zu 100 % kennen bevor ich antworte.
- **OWNER-GATE:** nichts nach außen ohne explizites „Ja".
- **Keine Beträge/Gagen** in Mails ohne Freigabe. **Keine Überweisung** je selbst auslösen.

## User

- **Dirk Wöhrle**, Geschäftsführer.
- **x-media music GmbH** — Musikagentur, Adresse Obere Str. 13, 70190 Stuttgart, Mail info@xmedia24.com, www.xmedia24.com, Mobil +49 176-42508631. Buchhaltung mit **DATEV**. Betreibt Band **Hofbräu-Regiment** (Top-Partyband Süddeutschland).
- **x-media event GmbH** — zweite Firma, gemeinsam mit **Alexander Doczi**. Betreibt **VIPS-Partyband** + eigene Events (viel Organisation).
- Arbeitet auf dem **Mac** (kein Outlook). Antwort-Stil: kurz, knapp.
- **Virtuelle Sekretärin:** Helen Sanders (i. A. von Dirk), KI-Fußnote **aus**.

## Project

- **Aktive Module:** Booking, Akquise (vorgebaut) + neu: Buchhaltung, Aufgaben/Fristen, Programme.
- **Buchhaltung LIVE (01.07.2026):** Mail-Anbindung Strato IMAP/SMTP (info@ + rechnung@) funktioniert; Belege werden aus rechnung@ gezogen, klassifiziert (lernende Tabelle), Mehrfach-PDFs zusammengeführt, nach Zahlweg an DATEV-Uploadmails weitergeleitet (Versand nur nach OWNER-GATE, Absender info@ ist bei DATEV freigeschaltet).
- **Gelernte Zahlwege:** STRATO/Telekom/UTA/Brevo → Bank (Lastschrift); Celonis → Kreditkarte Master; TS Veranstaltungstechnik + Daniela Metellus → Rechnungseingang (Überweisung). Details in `module/buchhaltung/datev_routing.csv`.
- **Automatik:** täglicher Auto-Check (~7:00, geplante Aufgabe „buchhaltung-check") prüft rechnung@ (offensiv) + info@ (konservativ mit Detektor) und legt Vorschläge vor. Läuft nur bei geöffneter App.
- **Bewirtungsbelege LIVE:** Erfassung per Mail (iPhone-Scan + diktierter Text) → `scripts/bewirtung.py` erzeugt Zusatzblatt + Merge → Routing bar→Kasse / EC→Bank. Firma über Empfängeradresse. End-to-end getestet 01.07.2026.
- **Offene Punkte:** event-Postfach `rechnung@xmedia-event.de` bei Strato einrichten (dann als 3. Postfach anbinden; event-Belege → Dropbox); event-Dropbox-Ordnerstruktur; Dateinamen-Schema music; Portal-Belege (Amazon/Facebook); iPhone-Kurzbefehl (nur am iPhone baubar — Scan-Aktion iOS-only).
- **Akquise LIVE (01.07.2026):** Modul konfiguriert (`module/akquise/akquise_config.md`) — 20 Leads/Lauf, Absender Helen Sanders, Regionen BaW/Bayern/RLP-Hessen/DACH, Event-Typen Vereinsfest/Zelt/Firmenevent/Stadtfest. Repertoire-Quellen je Band unter `module/akquise/repertoire/` (Hofbräu + VIPS, aus Setlist-PDFs). SMTP-Versand über `send_email.py` getestet + funktioniert.
- **Akquise-Runde 1 Hofbräu-Regiment (01.07.2026):** 18 Mails versendet, 1 Bounce (Feuerwehr Göggelsbuch — Domain existiert nicht, neue Adresse suchen). Kontaktierte in `bestandsliste.csv` (Status „kontaktiert 2026-07-01"). Sammelliste geleert. Wiedervorlage Rücklauf-Check = geplante Aufgabe `akquise-hofbraeu-ruecklauf-2026-07-15` (15.07.2026, 9:00).
- **Akquise-Runde 2 VIPS-Partyband (01.07.2026):** 17 Mails versendet, 0 Bounces. Absender/Signatur = **x-media music GmbH** (Dirk-Entscheid: VIPS wird als music-Agentur vermittelt, nicht als event GmbH). Kontaktierte in `bestandsliste.csv`. Wiedervorlage = `akquise-vips-ruecklauf-2026-07-15` (15.07.2026, 9:15). Bestandsliste jetzt 36 Orgs gesamt (19 Hofbräu + 17 VIPS).
- **Akquise-Runde 3 Hofbräu-Regiment (02.07.2026):** 30 Mails versendet, 0 Bounces, **mit Homepage-Link www.hofbraeu-regiment.de** (jetzt fester Mail-Baustein für Hofbräu, siehe akquise_config.md). Strengere Verifikation (Mail muss sichtbar auf Impressum stehen). Bestand jetzt **66 Orgs**. Wiedervorlage = `akquise-hofbraeu-r2-ruecklauf-2026-07-16` (16.07.2026, 9:00).
- **Groß-Runde (03.07.2026):** 100 Leads gesammelt (6 parallele Regionen-Läufe, strenge Impressum-Verifikation), Split 50 Hofbräu / 49 VIPS; auf Wunsch entfernt: Gruber Ellingen (Dublette), ARGE Plüderhäuser (schon in Kontakt). Versendet: **49 Hofbräu + 48 VIPS**, 1 Bounce (Blattlschoner Oberbeuren, Domain existiert nicht). **Bestand jetzt 164 Orgs.** Versand via Bulk-Sender `/tmp/bulk_send.py` (eine SMTP-Verbindung, viel schneller als Einzelaufrufe — bei großen Runden nutzen). Wiedervorlage = `akquise-grossrunde-ruecklauf-2026-07-17` (17.07.2026, 9:00).
- **Groß-Runde 2 (04.07.2026):** 100 Leads gesammelt (6 Regionen-Läufe), 2 Dubletten raus (MV Weingarten, Stiftl), MV Endersbach auf Wunsch entfernt. Versendet: **50 Hofbräu + 47 VIPS**, 0 Bounces. **Bestand jetzt 262 Orgs.** Wiedervorlage = `akquise-grossrunde2-ruecklauf-2026-07-18` (18.07.2026, 9:00). Finale Mail-Vorlage (Betreff „Musikalisches Highlight…", Team-Booking-Text, Homepage-Link, volle Signatur + Logo) im Einsatz.
- **event-Buchhaltung angebunden (02.07.2026):** Dropbox `XE Buchhaltung` verbunden, Routing-Karte `module/buchhaltung/event_routing.csv` (offen/bezahlt/Kasse/Master/Ausgang). 2 DIE-NEUE-107.7-Rechnungen (2260582 = 2.915,50 € + 2260584 = 547,40 €) in `XE offene Eingangsrechnungen` abgelegt + als offene Posten erfasst; **Skonto-Erinnerung 06.07.** (zahlbar bis 08.07., 2 % Skonto). event-Postfächer `info_event`/`rechnung_event` in mail.env + Scripts angebunden (rechnung@xmedia-event.de: 7 offene Juni-Rechnungen warten noch; info@xmedia-event.de sehr voll).
- **GEMA-Vergleiche + Anwaltskosten (02.07.2026):** Anwalt Ulrich Poser (Kanzlei Poser, Hamburg; `mobile@musiclawyers.de` / `maurer@rechtsanwalt-poser.de`) hat 2 GEMA-Vergleiche (Live-Sparten bis GJ2025) geschickt: je **15.000 € brutto, fällig 15.12.2026** — GmbH (Mitgl. 1036985) + **Dirk privat (Mitgl. 1048460, NICHT GmbH-DATEV)**. Beide in `offene_posten.csv`, **noch NICHT gegengezeichnet** → erst nach GEMA-Gegenzeichnung ablegen; DATEV-Upload entscheidet Dirk später. Wiedervorlage-Reminder `wiedervorlage-gema-vergleiche` (01.12.2026 9:00) + `module/aufgaben/aufgaben.csv`. GEMA-Bankverb.: IBAN DE02 7004 0041 0663 3333 04 (Commerzbank, COBADEFFXXX) — via OCR, vor Zahlung gegen PDF prüfen; Nachweis nach Zahlung an prevention@gema.de. — **Anwaltsrechnung RA Poser Rg 2600053 (3.310,29 €, IBAN DE94 3006 0601 0105 7507 76, apoBank DAAEDEDDXXX) am 02.07. an DATEV Rechnungseingang übergeben** (offener Posten, Überweisung durch Dirk). Absender in `datev_routing.csv` gelernt. **Neu: Aufgabenliste `module/aufgaben/aufgaben.csv`.**
- **✅ Angebot Radio L12 „Weinstadt" (2.450 € netto) — FREIGEGEBEN + GESENDET am 03.07.2026** an Tobias Hena (t.hena@dieneue1077.de) ab info@xmedia-event.de, signiertes PDF im Anhang. Wiedervorlage `wiedervorlage-angebot-weinstadt` deaktiviert. Nächster Schritt: Umsetzung/Abwicklung durch Radio L12; Ausgangsrechnung x-media event abwarten.
- **Mail-Automatik ausgebaut (03.07.2026):** (1) `send_email.py` legt jede gesendete Mail automatisch in „Sent Items" ab (`--no-save-sent` PFLICHT bei Akquise, `--save-sent-only` = Nachtrag). (2) `check_inbox.py` neu: `--with-body` + `--cursor-name`. (3) Scheduled Task **`morgen-briefing`** (tgl. 07:21): Triage 4 Postfächer + Vorgangs-Wächter (`module/aufgaben/aufgaben.csv`) + Antwort-Entwürfe (`module/entwuerfe/`) + Todoist. (4) Scheduled Task **`tagsueber-mail-waechter`** (stündl. 9–18 Uhr Mo–Sa): nur relevante neue Mails + Vorschlag. Beide senden NICHTS (OWNER-GATE). Belege bleiben beim Beleg-Check.
- **Todoist-Aufgaben-Übergabe (03.07.2026):** Connector verbunden, Projekt **„Für Claude"** (id `6h33QX2Rp3VQCM6j`). Dirk diktiert unterwegs hinein → ich lese/arbeite ab/kommentiere/hake ab. Fest ins Morgen-Briefing eingebunden (Testphase — bei Bedarf Schritt 7 im Task-Prompt entfernen).
- **Lead Musikverein Rommelshausen / Ladenburger (03.07.2026):** Florian Ladenburger (1. Vors., 1.vorsitzender@musikverein-rommelshausen.de) hakte via info@xmedia-event.de zu einer **107.7-Party** nach (Wunschtermin 5.5.2027). Antwort **gesendet 16:22** ab info@xmedia-event.de (Dirk persönlich, SIE): 5.5.2027 passt unsererseits, um Terminvorschläge für Besprechung gebeten. Akte `wissensbasis/R/Musikverein_Rommelshausen.md`, Wiedervorlage 03.08.2026 in `module/aufgaben/aufgaben.csv`. Hinweis: SMTP-Einzelversand lief in 45s-Timeout → besser im Hintergrund (`nohup … &`) starten und Log/Sent prüfen.
- **Multi-Mac / Hub-Host (03.07.2026, OFFEN — Dirk überlegt):** Projektordner via iCloud auf beiden Macs. Plan: stationären Mac (M1 Air ODER Mac mini) zum „Host" machen, der immer online bleibt und die Automatik laufen lässt; Haupt-MacBook = Bediengerät. Grundregel: Automatik NUR auf dem Host (sonst Doppelläufe + iCloud-Konflikte). Noch nicht eingerichtet — Dirk wählt noch den Host.

## Feedback

- UTA-Rechnungen: immer 3 PDFs → zu einem zusammenführen (Fahrzeug-Aufschlüsselung).
- „DG Projekt" = nur E-Mail-Alias von Daniela Metellus.
- DATEV Upload-Mail nimmt nur **freigeschaltete Absenderadressen** an — sonst stiller Verwurf.
- Bewirtung: **Zahlweg im Betreff ist maßgeblich** (nicht die Kartenzeile auf dem Beleg — evtl. privat gezahlt, Geld aus Kasse entnommen).
- Bewirtung/Firma: Trennung über die **Empfängeradresse** (music vs. event), nicht über den Betreff.
- Mail-Body auslesen: auch **inline** text/plain-Teile beachten (nicht nur disposition=None).
- **Top-Feste-Versand VERSCHOBEN auf Mittwoch 08.07.2026, 10:00** (Dienstag 07.07. läuft Dirks Newsletter): 55 Top-Feste (28 Hofbräu + 27 VIPS) in `dienstag_hofbraeu.csv` / `dienstag_vips.csv`, von Dirk freigegeben, Aufgabe `akquise-topfeste-versand-dienstag-2026-07-07` (fireAt jetzt 08.07. — Task-ID trägt noch "dienstag", Termin ist Mi). Rücklauf-Check 22.07. Danach Listen leeren.
- **Donnerstag-Versand geplant (09.07.2026, 10:00):** 50 Konkurrenz-Tannenbaum-Leads (25 Hofbräu + 25 VIPS) in `donnerstag_hofbraeu.csv`/`donnerstag_vips.csv`, geplante Aufgabe `akquise-konkurrenz-versand-donnerstag-2026-07-09`. Bewusst getrennt vom Dienstag-Versand (Zustellbarkeit). Rücklauf 23.07. Grund: 100+ Kaltmails/Tag von einer Adresse schaden der Reputation → auf 2 Termine verteilen.
- **Konkurrenzband-Liste = starke Tannenbaum-Quelle:** Dirk hat Liste `Konkurenz-Bands.csv` (31 Bands, u.a. Würzbuam, Allgäu Power, Nachtstark, Partyböcke, Frankenkracher, Hautnah, Dirndlknacker) geliefert. Deren Auftrittskalender → Veranstalter = hochwertige Volksfest-Leads. ALARM ist eine EIGENE x-media-Band (nicht Konkurrenz, nicht als Quelle nutzen).
- **Wasen-Tannenbaum funktioniert (04.07.2026):** Reverse-Tannenbaum über Konkurrenz-Partybands (deren Auftrittskalender → Veranstalter der Feste) liefert hochwertige Volksfest-Leads. Bands als Quelle, nie kontaktieren. Bewährte Fund-Bands: OHLALA, 7 Promille, Ois Easy, Draufgänger, Troglauer, voXXclub, Kapelle So&So. Festwirte-Multiplikator (Festwirt-Website listet alle seine Feste → Veranstalter) ebenfalls stark.
- **Auftritts-Konflikt-Check (08.07.2026):** Vor jedem Akquise-Versand die Auftrittsorte beider Bands abgleichen — Quelle `hofbraeu-regiment.de/termine` + `vips-partyband.de/termine` (ändern sich laufend, live prüfen). Regel: Band spielt dort → nur die ANDERE Band anbieten; beide spielen → Lead raus (Aktivkunde). Bekannte Fälle in `module/akquise/band_auftritte.md`: Koblenzer Oktoberfest→nur VIPS; Heiner Wiesn/Wernau/BOF Freiburg/Schwäbisch Gmünd→raus; Oktoberfest Leipzig/Dorsten/Waldshuter Chilbi→nur Hofbräu.
- **Wasen-Exklusivität (04.07.2026):** Hofbräu-Regiment = Exklusivvertrag Zelt „Beim Benz" auf dem Cannstatter Wasen → KEINE anderen Wasen-Festzelte kontaktieren (Wasenwirt, Göckelesmaier, SchwabenWelt, Klauss&Klauss usw.). Wasen-Zelte NUR als Tannenbaum-Quelle nutzen (dort spielende Bands → deren Gigs → neue Veranstalter). Regel in `akquise_config.md`.
- **Akquise-Zielprofil geschärft (04.07.2026):** Qualität vor Nähe — Priorität Festwirte/Zeltbetreiber > große Volks-/Wein-/Straßenfeste > Stadtfeste/Kommunen > Vereinsfeste (nur mit Partyband-Slot). Pflichtfilter: erkennbarer Party-/Live-Slot, keine reinen Blasmusik-Vereine, bekannte/große Feste bevorzugen. Geo breit inkl. Thüringen/Sachsen/NRW, Fest-Stärke schlägt Geografie. Band gemischt 50/50. Referenz-Kaliber: Augsburger Plärrer, Gäubodenfest. Details in `module/akquise/akquise_config.md`.
- **Akquise-Mailstil (02.07.2026):** Helen Sanders = „Team Booking" (kein „Sekretärin", Dirk nicht namentlich im Text, nur ein Name). Einstieg „…weil wir denken, dass [Band] hervorragend zu Ihren Festen passt…". Homepage-Link je Band Pflicht-Baustein. Details in `module/akquise/akquise_config.md`.
- **Bilder/Dateien vom User** kommen NICHT an, wenn sie in den Chat eingefügt werden — Austausch über einen angebundenen Ordner (z. B. `Documents/Claude/Projects/Uploads` oder Dropbox). Dirks **Unterschrift + Firmenstempel** (music & event) liegen in `…/Projects/Uploads/` (Unterschrift-Dik Wöhrle.png, Stempel x-media event/music 2020.png) — für digitales Signieren von Dokumenten (Überlagern via reportlab+qpdf; PNGs haben transparenten Hintergrund).

## Reference

- Regeln: `.claude/rules/` (00_core, 01_booking, 02_akquise, 03_buchhaltung, 04_aufgaben_fristen, 05_programme)
- Buchhaltung: `module/buchhaltung/` (datev_routing.csv, offene_posten.csv, verarbeitet.csv, ignorieren.csv, eingang/, eingang_info/)
- Scripts: `scripts/` (check_inbox.py, send_email.py, dashboard.py, ist_rechnung.py; Zugang in mail.env)
- Dashboard: `reports/dashboard.html` (via `python3 scripts/dashboard.py`)
- **E-Mail-Signaturen:** `module/signaturen/signatur_music.html` + `signatur_event.html` (echte Firmen-Signaturen, Logo `logo.png` 105×79 px). Versand mit Logo: `send_email.py … --inline logo=module/signaturen/logo.png`. Hinweis: Mail-Clients richten sich nach der echten Pixelgröße des Logos (CSS-Höhe wird teils ignoriert) → Größe über die Bilddatei steuern.
- Vorgefertigte Mantel-Memories: `memory/` (siehe `memory/MEMORY.md`)
- **CRM-Datenbank-Zugang (Supabase):** Steuerung/Auslesen des CRM direkt möglich. Details + Keys in `wissensbasis/C/CRM-Datenbank-Zugang.md`. Service-Role-Key liegt gitignored in `scripts/crm_keys.env` (Projekt-Ref `vrntqlmrxlbnhetskwjw`). CRM-Frontend nutzt native `confirm()`-Dialoge → Löschen/Schreiben besser direkt über DB/API statt UI-Button.
- **Buchhaltungsassistent (Supabase, Projekt-Ref `hsvpjtpzsnfdpibdkxut`):** war deaktiviert, am 02.07.2026 reaktiviert. Enthält echten Bestand (171 Belege, 194 PDFs, 471 Protokoll, 96 Regeln). Service-Role-Key gitignored in `scripts/buchhaltung_keys.env`. **Vollständiges Backup:** `backups/buchhaltung_export_2026-07-02/` (7 Tabellen JSON+CSV + 194 Dateien, 51 MB). Löschung des Projekts steht noch aus (Dirk prüft Backup zuerst). Belege liegen laut Dirk ohnehin in DATEV/auf Platte (nur Durchschleusung).

---

## Pre-Seed: Universal-Mantel-Memories

In `memory/` liegen 14 vorgefertigte Mantel-Memories (Mindset, Externe Kommunikation, Hub-Disziplin) — siehe `memory/MEMORY.md`. Direkt nutzbar, anpassbar, löschbar.

---

## Stand 17.07.2026 (Morgen-Briefing + Nachlauf)

**Postfächer:** info@ heute wieder lesbar (Timeout vom 16.07. trat nicht auf), 4/4 gescannt ab 15.07.
INBOX info@ hat weiterhin ~48.000 Mails → Aufräumen bleibt empfohlen (Timeout-Risiko).

**Todoist wieder LIVE:** Connector war entfernt (nicht defekt) — Dirk hat am 17.07. neu autorisiert.
Konto x-media/info@xmedia24.com (Pro), Projekt-IDs unverändert. 15 offene Aufgaben gespiegelt;
alle 68 OFFENEN Zeilen tragen jetzt einen `[TD:]`-Marker. „Für Claude": leer.

**Gelernt (in Regeln/Skripte einbauen — Task 20.07.):**
- **CSV-Feldzahl-Check (Soll 6) ist Pflicht.** Ein Semikolon **im Titel** verschiebt alle Spalten →
  Zeile wird in jeder Auswertung unsichtbar. Am 17.07. betraf das **FF Göggelsbuch (22.07., OFFEN)** —
  wäre nie in einem Briefing aufgetaucht. Repariert; Titel dürfen kein `;` enthalten.
- **`[TD:]`-Filter per Regex** auf echte Marker prüfen, nicht auf Textvorkommen — sonst fällt eine
  Task raus, weil ihr Notiztext „[TD:" enthält (genau so passiert).

**Neue Wissensbasis-Einträge:**
- `R/Riecker-Gernot.md` — Gernot Riecker = `griecker@t-online.de`, befreundeter Fotograf,
  Stammlieferant für Bandfotos, liefert per WeTransfer (Links laufen ab). Nicht = Nadine Bayer.
- `B/Buchhaltungs-App_ruht.md` — Buchhaltungs-Automatisierung **ruht bewusst**.
  `buchhaltung.xmedia24.com` ist offline = **so gewollt**, in Hostinger-Warnungen ignorieren.
  **Befund:** Supabase-Backend löst nicht mehr auf → Zugänge in `buchhaltung_keys.env` vermutlich tot
  (Task 20.07.: Dashboard prüfen). Produktiver Beleg-Weg NICHT betroffen.

**Geklärt / nicht mehr nachfragen:**
- **Nameserver** bleiben bei Strato — keine Umstellung gewünscht. Sites laufen korrekt über A-Record
  auf der neuen Hostinger-IP 82.198.226.80 (verifiziert, HTTP 200).
- **„Alfred"** wird vom Briefing **nicht** informiert — es gibt keinen Kanal dorthin. Wer/was Alfred ist,
  ist ungeklärt (Spur: `_dach/COWORK-START-SNIPPET.md`, liegt außerhalb der freigegebenen Ordner).
  Dirk am 17.07.: vorerst nicht weiterverfolgen.

**Offene Loops mit datierter Aufgabe** (alle in aufgaben.csv + Todoist):
Todoist-Restarbeiten 20.07. · Claude-API ohne Guthaben 17.07. · Plausible-Trial 17.07. ·
Supabase Buchhaltungs-App 20.07.
