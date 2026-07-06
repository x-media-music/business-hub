# Akquise — Lead-Recherche, Kaltakquise, Reaktivierung

Gilt für: Lead-Recherche (Tannenbaum-Prinzip), Kaltakquise, Follow-ups, Reaktivierungen, Kontaktformulare

---

## AUTONOMIE-REGEL (KRITISCH!)

**Die gesamte Sammelphase läuft VOLLSTÄNDIG AUTONOM.**
- KEINE Rückfragen an `Dirk Wöhrle` während der Recherche
- KEINE Zwischen-Bestätigungen einholen
- Einfach starten und durcharbeiten bis zur Zielzahl
- **Doppelkontakt gewünscht:** Wer Kontaktformular UND Email hat, bekommt BEIDES
- **NUR der Versand (Phase 5) braucht das OWNER-GATE.** Alles davor ist autonom.

---

## ABSOLUTE STOP-REGELN

1. **NIE Preise/Gagen nennen** — Interesse aufbauen; fragt der Kunde nach dem Preis → `Dirk Wöhrle` übernimmt.
2. **NIE aktive Kunden anschreiben** — Mehrfach-Check vor jedem Lead: Gig gebucht? Laufende Verhandlung? Letzter Kontakt < 3 Monate? Auf Sperrliste? Schon Kunde dieses Jahr? → bei einem JA: STOP.
3. **NIE Wettbewerber-Künstler kontaktieren** — wir recherchieren ÜBER andere Künstler/Bands, kontaktieren aber **ausschließlich Veranstalter / Venues / Vereine**. Künstler = Mitbewerber!
4. **Backup vor JEDER Aktion** → `/Users/dirkwoehrle/Documents/Claude/Projects/business_hub_Dirk_STARTER/backups/`

---

## TANNENBAUM-PRINZIP (Schneeball-Lead-Recherche)

Das Herz der Akquise: aus einem Startpunkt wächst der „Tannenbaum" immer weiter — jeder Ast liefert neue Äste.

- **Chain Reaction VORWÄRTS:**
  `Künstler → Tourdaten → Venues → Veranstalter → Impressum → LEAD`
- **Chain Reaction RÜCKWÄRTS:**
  `Veranstalter → welche Künstler treten dort auf? → deren Tourdaten → neue Venues → neue Veranstalter → …`

Vorwärts und rückwärts abwechselnd fahren, bis die Zielzahl erreicht ist oder keine neuen Treffer mehr kommen.

**Rückverfolgung (INTERN — NIE in Emails!):**
- WO gefunden? (Quelle: Künstler-Website, Tourkalender …)
- WANN gefunden? (Datum)
- ÜBER WELCHEN PFAD? (max. 2–3 Schritte, kurz)
- Die Tour-/Wettbewerbsanalyse ist **vertraulich** — nie nach außen kommunizieren.

---

## SAMMELKORB-PRINZIP (drei Listen)

| Datei | Zweck | Verhalten |
|-------|-------|-----------|
| `sammelliste.csv` | Aktuelle Runde, frisch gesammelte Leads | **temporär** — wird nach dem Versand geleert |
| `bestandsliste.csv` | Alle je kontaktierten Leads | **wächst** dauerhaft |
| `bestandsliste_telefon.csv` | Leads mit NUR Telefon (kein Kontaktweg schriftlich) | **geparkt** |

Ablage: `/Users/dirkwoehrle/Documents/Claude/Projects/business_hub_Dirk_STARTER/module/akquise/kontakte/`

---

## 8-PHASEN-WORKFLOW

### Phase 0: Sicherheitsnetz
1. Backup ziehen (Kontakte + Kalender)
2. Komplett-Abgleich: Kontakt-Bestand ↔ `bestandsliste.csv` ↔ `bestandsliste_telefon.csv` ↔ `sammelliste.csv`
3. Inkonsistenzen fixen

### Phase 1: Sammlung (autonom, bis Zielzahl)
- Tannenbaum VORWÄRTS + RÜCKWÄRTS fahren (siehe oben)
- **STOP-Kriterien:** Zielzahl erreicht · keine neuen Treffer mehr · Endlosschleife erkannt
- **Live-Check** jeder Lead gegen den bestehenden Kontakt-Bestand
- **Qualitätsfilter:** Email vorhanden? Passender Event-Typ? Zielregion? Passt der Künstler dazu?
- **Impressum-Check PFLICHT (Veredelung):** Footer „Impressum / Kontakt / Über uns" auswerten → Name, Email, Telefon, Entscheider ermitteln

### Phase 2: Interner Abgleich (Dedup)
- `sammelliste.csv` vs. `bestandsliste.csv` → Duplikate entfernen
- `sammelliste.csv` vs. `bestandsliste_telefon.csv` → Duplikate entfernen

### Phase 3: Bestandsabgleich (Daten-Update)
- `sammelliste.csv` vs. Kontakt-Bestand
- Schon im Bestand? → aus `sammelliste.csv` entfernen
- ABER: Daten aktualisieren (neue Email, neuer Ansprechpartner, neues Telefon) + Notiz

### Phase 4: Erreichbarkeit herstellen
- **4a — Kontaktformulare (Bot):** Leads MIT Formular aber OHNE Email → Auto-Fill + Submit über den Formular-Bot
- **4b — Email-Nachrecherche:** Leads OHNE Email + OHNE Formular, aber Ansprechpartner bekannt → gezielt Email suchen (Name + Organisation, berufl. Netzwerke, Lokalpresse)
- **4c — Telefon-Parken:** nur Telefon verfügbar → nach `bestandsliste_telefon.csv`; gar kein Kontaktweg → verwerfen

### Phase 5: Versand (⚠️ OWNER-GATE!)
- Emails vorbereiten — **NICHT senden!**
- `Dirk Wöhrle` zeigen: Anzahl, Liste (Empfänger + Betreff), Beispiel-Email
- [JA] alle senden / [NEIN] abbrechen / [EINZELN] jede prüfen

### Phase 6: Verschieben
- versendete Leads: `sammelliste.csv` → `bestandsliste.csv`
- `sammelliste.csv` = LEER

### Phase 7: Report + Neustart
- Zusammenfassung: neue Leads, Duplikate, Updates, ausgefüllte Formulare, versendete Emails
- Neuer Startpunkt? → zurück zu Phase 0

---

## DUPLIKAT-CHECK (4-FACH)

1. Kontakt-Bestand (Backup) → SKIP wenn vorhanden
2. `bestandsliste.csv` → SKIP
3. `bestandsliste_telefon.csv` → SKIP
4. `sammelliste.csv` (aktuelle Runde) → SKIP

**ABER:** immer Datenvergleich! Neue Email? Neuer Ansprechpartner/Vorsitzender? → Bestand aktualisieren + Notiz.

---

## BOUNCE-HANDLING + ANTWORT-VERARBEITUNG

| Typ | Aktion |
|-----|--------|
| Unzustellbar (Bounce) | Notiz „EMAIL UNZUSTELLBAR" + neue Adresse recherchieren |
| Absage (feste Kooperation) | Wiedervorlage 12–15 Monate |
| Absage (kein Budget) | Wiedervorlage 6 Monate |
| Absage (kein Event) | Wiedervorlage 12 Monate |
| Absage (kein Interesse) | keine Wiedervorlage |
| Info-Antwort (falscher Kontakt) | richtigen Ansprechpartner recherchieren + kontaktieren |
| Verweis auf Dritten (z. B. Veranstalter des Festes) | alle Betreiber/Beteiligten des Events recherchieren |

**⚠️ Wiedervorlagen NIE als Eintrag im Buchungskalender!** Jede Wiedervorlage → **Aufgaben-/Task-Liste** (Fälligkeitsdatum + Kategorie „Wiedervorlage"), Inhalt in die Akte (Kontaktnotiz + Wissensbasis). Der Buchungskalender bleibt sauber für echte Buchungen.

---

## GEO-QUOTA + EVENT-BALANCE (projektspezifisch anpassen)

Verteilung von Zielregionen und Event-Typen als Vorgabe hinterlegen, damit die Sammlung ausgewogen bleibt (z. B. mehrere Regionen anteilig, Mischung aus Vereinsfesten und Festival-/Zeltbetreibern). Konkrete Prozentwerte in den projekteigenen Defaults setzen.

---

## REPERTOIRE-BEISPIELE IN WERBEMAILS (PFLICHT-SCHRITT)

**Bei JEDER Werbemail mit Repertoire-Bezug:** Beispiel-Titel/-Acts IMMER aus der kanonischen Setliste/Programmliste des jeweiligen Künstlers ziehen — **NIE aus dem Kopf zusammenstellen** (Gefahr: falsche oder nicht aktuelle Titel).

- 5–8 prägnante, zielgruppengerechte Beispiele daraus zitieren.
- **Künstler nicht vermischen** — Beispiele eines Acts gehören nicht in die Mail eines anderen.

---

## DATEIEN

| Datei | Zweck | Pfad |
|-------|-------|------|
| `sammelliste.csv` | temporär (wird geleert) | `module/akquise/kontakte/` |
| `bestandsliste.csv` | alle kontaktierten Leads (wächst) | `module/akquise/kontakte/` |
| `bestandsliste_telefon.csv` | Telefon-only Leads (geparkt) | `module/akquise/kontakte/` |
| `akquise_counter.csv` | Statistik | `module/akquise/kontakte/` |
| `email_progress.json` | Versand-Fortschritt | `module/akquise/kontakte/` |

---

## SCRIPTS (generisch)

| Script | Zweck |
|--------|-------|
| `kontakte/formular_bot.py` | Kontaktformular-Bot (Auto-Fill + Submit, Captcha-Handling) |
| `kontakte/impressum_check.py` | Impressum-Check / Veredelung (Kontaktdaten aus Footer) |
| `kontakte/check_inbox.py` | Inbox checken, Antworten kategorisieren, Bounces erkennen |
| `kontakte/email_sender.py` | Emails versenden (nach OWNER-GATE) |
| `kontakte/bestand_abgleich.py` | Kontakt-Bestand abgleichen + Dedup |
| `reaktivierung/run.py` | Reaktivierungs-Hauptloop |
| `reaktivierung/bounce.py` | Bounce-Handling |
