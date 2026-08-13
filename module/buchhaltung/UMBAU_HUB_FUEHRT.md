# Buchhaltung — Umbau „Hub führt, App zeigt + gibt frei"

**Beschlossen:** 11.08.2026 (Dirk) · **Status:** in Umsetzung
**Ersetzt:** die App-Übernahme vom 03.08.2026 (App war führend, Hub nur READ-ONLY-Wächter)

---

## WARUM

Der App-/n8n-Betrieb lief nicht zufriedenstellend: n8n-Mailimport stand seit
03.08.2026 (8 Tage nichts erfasst), Klassifizierung/Routing unzuverlässig,
Belege blieben liegen. Dirk dreht die Führung zurück zum Hub.

---

## ZIELBILD

| Rolle | Wer | Was |
|---|---|---|
| **Führung / Verarbeitung** | **Hub (Claude)** | Postfächer ziehen, Rechnung erkennen, Box zuordnen (lernend), Mehrfach-PDFs mergen, standardisiert benennen, Beleg in `bh_belege` schreiben (Status „warte_bestaetigung") |
| **Anzeige + Freigabe** | **App** (buchhaltung.xmedia24.com) | Zeigt die vom Hub vorbereiteten Belege als Karten mit Buttons (Freigeben / Ablehnen / Box ändern / schon erledigt) → setzt nur `dirk_entscheidung` |
| **Versand nach Freigabe** | **Hub** | Holt freigegebene Belege, sendet an DATEV-Uploadmail (Music) bzw. verschiebt in Dropbox (Event), setzt Status „verarbeitet" + Protokoll |

**Eine einzige Pipeline = der Hub.** Kein n8n-Ingest, kein KI-Routing in der App mehr.

---

## ENTSCHEIDUNGEN (11.08.2026)

1. **Versand:** Der **Hub** sendet nach Freigabe (nicht die App/n8n) — unabhängig von n8n.
2. **n8n-Import:** wird **abgeschaltet**; nur der Hub zieht die 4 Postfächer.
3. **Rhythmus:** Hub-Lauf **4× täglich — 10:00, 13:00, 15:00, 18:00**.
4. **Freigabe-Kanal Übergang:** **erst Chat-Freigabe** (OWNER-GATE im Chat), App-Umbau danach.

---

## PIPELINE (Soll)

```
[10/13/15/18 Uhr Scheduled Task]
  → bh_ingest.py
      ├ check_inbox.py: rechnung@ / info@ (music) + rechnung@ / info@ (event) inkrementell
      ├ ist_rechnung.py: Rechnung? (rechnung@ offensiv, info@ konservativ)
      ├ Routing: datev_routing.csv (music→DATEV-Box) / event_routing.csv (event→Dropbox-Ordner)
      ├ Mehrfach-PDF-Merge (UTA 3 PDFs, Boss 3 PDFs, …)
      ├ Standard-Dateiname + PDF in Supabase Storage
      └ INSERT bh_belege: status='warte_bestaetigung', erstellt_von='hub', Box-Vorschlag, Betrag, Absender, Rg-Nr
            (Dedup über pdf_hash / rechnungsnummer gegen Bestand)
  → Report + Chat-Freigabe-Block an Dirk (Übergangsphase)

[Dirk gibt frei — Chat "ja"/"senden", später App-Button]
  → dirk_entscheidung='freigegeben' (+ dirk_entschieden_am)

  → bh_send.py (nächster Lauf)
      ├ SELECT bh_belege WHERE dirk_entscheidung='freigegeben' AND status<>'verarbeitet'
      ├ Music → send_email.py an DATEV-Uploadmail (Box aus datev_kategorie)
      ├ Event → Datei nach Dropbox-Zielordner kopieren/verschieben
      ├ status='verarbeitet', verarbeitet_am gesetzt
      └ bh_protokoll: aktion='versendet'/'verschoben', automatisch=false, benutzer='dirk-freigabe'
```

### Sonderfall stehende Freigaben
- **UTA Edenred (Tankkarte):** stehende Freigabe (Dirk 21.07.2026) → darf autonom an Bank-Uploadmail, ohne Einzel-Gate; im Report weiter ausweisen.

---

## RELEVANTE FELDER in `bh_belege`

`status` (eingegangen/klassifiziert/warte_bestaetigung/verarbeitet/fehler) ·
`dirk_entscheidung` (freigegeben/abgelehnt/schon_erledigt/firma_geaendert) ·
`dirk_entschieden_am` · `dirk_kommentar` · `erstellt_von` (neu: 'hub') ·
`datev_kategorie` (bank/rechnungseingang/kreditkarte_master/kasse/rechnungsausgang) ·
`datev_email` · `dropbox_ordner` · `firma` (music/event) · `zahlungsstatus` ·
`pdf_hash` (Dedup) · `pdf_final_path` / `pdf_storage_path`

---

## MIGRATIONSSCHRITTE

1. ✅ **Backup** bh_belege (290 Belege) + Routing-CSV → `backups/` (11.08.2026)
2. ✅ **Plandokument** (dieses File)
3. ✅ **bh_ingest.py** gebaut + live erprobt (11.08.) — zieht 4 Postfächer, Dedup (pdf_hash + RgNr), UTA-Merge + Auto-Freigabe, Bewirtung-Skip, unbekannte Absender → „Box in App wählen". Cursor: `module/buchhaltung/ingest_cursor.json`.
4. ✅ **bh_send.py** gebaut + live erprobt (11.08.) — liefert freigegebene ab Go-Live an DATEV/Dropbox, idempotent (verarbeitet_am), Stichtag-Sperre schützt Altlasten.
5. ⬜ **n8n abschalten** (Ingest + DATEV-Routing) via xmedia-n8n-Skill — OFFEN. n8n-Ingest steht ohnehin seit 03.08. still (interferiert aktuell nicht); sauber deaktivieren + dokumentieren.
6. ✅ **Scheduled Task** `buchhaltung-check` auf 4×/Tag (10/13/15/18) umgestellt — ingest + send + Report (11.08.).
7. ⬜ **App-Umbau** zum reinen Anzeige-/Freigabe-Tool (KI/n8n-Routing raus) — später.

**Live-Erprobung 11.08.2026 (erfolgreich end-to-end):** STRATO, UTA, 3× Mediapool, Apple vorbereitet → Dirk in App freigegeben → Hub an DATEV/Dropbox ausgeliefert. Dirk hat Fehlerkennungen (L-Events-Rider) in der App abgelehnt, Anschreiben als „schon erledigt" markiert. Modell funktioniert.

**Offene Altlasten (vor Go-Live freigegeben, nie ausgeliefert — bh_send fasst sie NICHT an, Dirk entscheidet):**
Getränke Zehnder 1.277,51 € (event) · Emily Woehrle 500 € (event) · Brevo SIB-5567711 55 € (music).

---

## ROLLBACK

- Backups in `backups/bh_belege_*.json` (Wiederherstellung per Supabase-Upsert möglich).
- n8n-Workflows werden nur **deaktiviert**, nicht gelöscht → jederzeit reaktivierbar.
- Umschaltung erst nach erfolgreichem Parallellauf.

---

## ABSOLUTE REGELN (unverändert)

- **OWNER-GATE** vor jedem DATEV-Versand / Dropbox-Move (Chat-Freigabe = das Gate; später App-Button).
- **Keine Zahlung/Überweisung** durch den Hub — nur Beleg-Weiterleitung, Dirk zahlt selbst.
- **Backup vor jeder schreibenden Aktion.**
- Bei Unsicherheit über die Box → Dirk fragen, lernen in `datev_routing.csv`.
