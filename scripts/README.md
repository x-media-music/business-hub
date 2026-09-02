# Scripts — Mail-Werkzeugkasten (Strato IMAP/SMTP)

Die Mail-Scripts laufen über **Strato IMAP/SMTP** (Postfächer info@ + rechnung@
xmedia24.com). Nur Python-Standardbibliothek — keine Zusatzpakete nötig.

## Was hier liegt

| Datei | Zweck | Status |
|---|---|---|
| `mail_config_template.env` | Vorlage für Strato-Zugangsdaten | Vorlage |
| `mail.env` | echte Zugangsdaten (Passwörter) — **lokal, gitignored** | Passwörter eintragen |
| `send_email.py` | Mail-Versand über SMTP (Gate-Hash, Office-Guard, Logging) | ✅ produktiv |
| `check_inbox.py` | Inbox-Check über IMAP (Cursor, Anhang-Download) | ✅ produktiv |
| `azure_app_template.env`, `refresh_token.py` | Alt-Reste MS-Graph | nicht mehr genutzt |

## Einrichtung (einmalig)

1. `scripts/mail.env` öffnen (liegt schon bereit) und die **zwei Passwort-Zeilen**
   ausfüllen:
   - `MAIL_INFO_PASSWORD=` → Passwort von info@xmedia24.com
   - `MAIL_RECHNUNG_PASSWORD=` → Passwort von rechnung@xmedia24.com
   - Datei speichern. Sie ist in `.gitignore` — bleibt lokal.
2. Verbindungstest (liest nur, sendet nichts):
   ```
   python3 scripts/check_inbox.py --from rechnung --since 2026-06-01
   ```

## Strato-Serverdaten (in mail.env hinterlegt)

| | Server | Port | Verschlüsselung |
|---|---|---|---|
| IMAP (lesen) | imap.strato.de | 993 | SSL/TLS |
| SMTP (senden) | smtp.strato.de | 465 | SSL/TLS |

Login = volle E-Mail-Adresse + Postfach-Passwort.

## Postfächer (Stand 16.08.2026)

| `--from` | Adresse | Nutzung |
|---|---|---|
| `info` | info@xmedia24.com | Korrespondenz music — lesen **+ senden** |
| `rechnung` | rechnung@xmedia24.com | Belege music — lesen + senden (DATEV) |
| `info_event` | info@xmedia-event.de | Korrespondenz event — lesen + senden |
| `rechnung_event` | rechnung@xmedia-event.de | Belege event — lesen + senden |
| `ninox` | ninox@xmedia24.com | Ninox-Versandweg — **NUR LESEN** |
| `anfrage` | anfrage@xmedia24.com | CRM-Versandweg — **NUR LESEN**, hier laufen auch Kunden-Rueckfragen ein |

**ninox@ und anfrage@ sind bewusst nur in `check_inbox.py` verfügbar, nicht in
`send_email.py`.** Über diese Adressen versenden Ninox bzw. das CRM — der Hub
liest den Ausgang nur mit, damit der Stand-Check nicht nachfasst, was längst
raus ist. Dafür ist `--folder sent` der wichtige Aufruf:

**Wichtig — zwei Quellen, zwei Rollen:**

- **anfrage@** ist der eigentliche CRM-Versandweg. Im **Posteingang** landen die
  Kunden-Rueckfragen auf Angebote/Vertraege sowie die Formular-Anfragen von
  hofbraeu-regiment.de. Fuer den Stand-Check die wichtigste Quelle.
- **ninox@** bekommt von jeder ueber anfrage@ verschickten Mail eine Kopie in den
  **Posteingang** (nicht in den Gesendet-Ordner) — das Archiv des CRM-Ausgangs.

```
python3 check_inbox.py --from anfrage --since 2026-08-01   # Kunden-Rueckfragen
python3 check_inbox.py --from ninox   --since 2026-08-01   # CRM-Ausgang (Archiv)
```

Strato benennt den Gesendet-Ordner je Postfach unterschiedlich
(`info@`/`rechnung@` = "Sent Items", `anfrage@` = "Sent"). `--folder sent`
erkennt das seit 16.08.2026 automatisch.

## check_inbox.py — Beispiele

```
python3 check_inbox.py --from rechnung                    # neue seit letztem Mal
python3 check_inbox.py --from info --since 2026-06-01      # ab Datum
python3 check_inbox.py --from rechnung --between 2026-06-01..2026-06-30
python3 check_inbox.py --from rechnung --save-attachments module/buchhaltung/eingang
python3 check_inbox.py --from rechnung --cursor-show
```

- Liest **read-only** — markiert keine Mail als gelesen.
- Cursor („neue seit letztem Mal") liegt in `backups/inbox_state.json`.
- `--save-attachments` speichert PDFs etc. — ideal für Belege aus rechnung@.

## send_email.py — Beispiele

```
python3 send_email.py --from info --to kunde@extern.de \
    --subject "Betreff" --body-file entwurf.html \
    --absender sekretaerin --gate-hash <md5>
```

- **OWNER-GATE-Disziplin:** `--gate-hash` = MD5 des freigegebenen Bodys. Wird der
  Text danach geändert, passt der Hash nicht mehr → Versand blockiert.
  Erzwingbar: `HUB_REQUIRE_GATE_HASH=1`.
- **Office-Guard:** `.docx/.xlsx/.pptx` an Externe wird blockiert (→ PDF senden
  oder `--allow-office`).
- `--dry-run` baut die Mail nur zusammen und zeigt den MD5, **ohne zu senden**.
- Versand wird in `logs/email_versand.log` protokolliert.

### Gesendet-Kopie (Ausgangsbox)

Nach jedem erfolgreichen Versand legt das Script **automatisch eine Kopie im
Gesendet-Ordner** des Absender-Postfachs ab (per IMAP, Strato-Ordner „Sent Items").
So sieht Dirk jede Hub-Mail ganz normal in seiner Ausgangsbox — für music und event.

- **`--no-save-sent`** → KEINE Kopie ablegen. **PFLICHT für Tannenbaum-/Akquise-
  Massmails** (die sollen die Ausgangsbox nicht zumüllen).
- **`--save-sent-only`** → NICHT per SMTP senden, nur eine Kopie in den Gesendet-
  Ordner legen (Nachtrag, falls eine Mail mal ohne Kopie rausging).
- Schlägt die Kopie fehl, ist die Mail trotzdem zugestellt (Kopie ist Nebensache);
  der Fehler wird nur geloggt.

## Sicherheit

- `scripts/mail.env` ist in `.gitignore` — niemals in ein Repo pushen oder teilen.
- Bei Verdacht auf Kompromittierung: Postfach-Passwort bei Strato ändern und in
  `mail.env` aktualisieren.
