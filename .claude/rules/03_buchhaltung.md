# Buchhaltung / Belege — Eingangsrechnungen, Belege, DATEV

Gilt für: Eingangsrechnungen (Musiker, Geschäftspartner, technische Dienstleister),
laufende/wiederkehrende Rechnungen, Belege sammeln (Amazon, Facebook, sonstige
Portale), Belegsortierung, Überweisungs-Vorbereitung, Übergabe an DATEV.

> ⭐ **Dirks größter Zeitfresser.** Erstes echtes Projekt nach dem Onboarding.

---

## GRUNDPRINZIP

- **OWNER-GATE vor JEDER Außenwirkung:** Beleg an DATEV weiterleiten, Datei
  verschieben, Überweisung auslösen. **Vorbereiten/Sortieren ist frei —
  Auslösen braucht Dirks JA.**
- **NIE eine Überweisung selbst auslösen** (Absolute Regel 4). Ich bereite nur
  die Übersicht vor (Empfänger, IBAN, Betrag, Zweck, Fälligkeit).

---

## EINGANG — zentrale Rechnungs-Mailadresse

- **rechnung@xmedia24.com** — hier laufen die **Musikerrechnungen** und die
  Rechnungen der **Geschäftspartner** auf.
- Dirk leitet die Rechnungen per **DATEV Upload** weiter — entweder über die
  **DATEV-App** oder per **E-Mail-Link** an die passende DATEV-Uploadmail.

---

## DATEV UPLOADMAIL-ADRESSEN — x-media music GmbH

| Kategorie | Uploadmail-Adresse |
|---|---|
| **Bank 405070673** | `06aa928a-7817-4bcf-a4ef-c2185efe6c35@uploadmail.datev.de` |
| **Rechnungseingang** | `5cc1bdc1-f56a-4718-b6da-325b7939246d@uploadmail.datev.de` |
| **Kreditkarte Master** | `abd46470-258e-4ebd-92d2-4c18b26fe595@uploadmail.datev.de` |
| **Kasse** | `868708a5-cb99-4ab3-ae70-0c71199e0f8a@uploadmail.datev.de` |
| **Rechnungsausgang** | `9616a328-2fcb-4f57-8df0-768c803106c7@uploadmail.datev.de` |

> **⚠️ Adress-Update 03.08.2026:** DATEV hatte einen internen Fehler; die Uploadmail-Adressen für **Rechnungseingang, Kreditkarte Master, Kasse und Rechnungsausgang** wurden neu vergeben (von Dirk bestätigt + mit den DATEV-Zieladress-Mails gegengeprüft). **Bank** (`06aa928a-…`) ist unverändert. Alte Adressen (b967094d / 7dd27b65 / 1dca708b / 00c798b5) NICHT mehr verwenden.


---

## ROUTING-LOGIK (final)

Belege gehen **nach Zahlweg** an die passende Box:

| Belegart / Zahlweg | Ziel-Uploadmail |
|---|---|
| Offene Musiker-/Dienstleister-/Geschäftspartner-Rechnung (noch **zu bezahlen**) | **Rechnungseingang** |
| Wiederkehrend, per **Lastschrift vom Bankkonto** abgebucht | **Bank** |
| Per **Mastercard** abgebucht | **Kreditkarte Master** |
| Barbeleg | **Kasse** |
| Eigene Ausgangsrechnung | **Rechnungsausgang** |

---

## LERNENDE ZUORDNUNG (Absender → Box)

Der Hub merkt sich pro Rechnungssteller, wohin der Beleg gehört, damit Dirk
nicht jedes Mal neu entscheiden muss.

- **Datei:** `module/buchhaltung/datev_routing.csv`
  (Spalten: `Rechnungssteller;Zahlweg;Zielbox;Notiz`, Semikolon/UTF-8)
- **Ablauf:**
  1. Neuer Beleg → Rechnungssteller in `datev_routing.csv` nachschlagen.
  2. **Bekannt** → Ziel-Box steht fest, direkt in den Gate-Block (Vorschlag) übernehmen.
  3. **Unbekannt** → Dirk **einmalig** fragen: „Welche Box?" → Antwort sofort in
     die CSV schreiben (lernen). Ab dann automatisch.
- Der eigentliche DATEV-Versand bleibt **immer hinter dem OWNER-GATE**.
- Ändert sich ein Zahlweg (z. B. Anbieter wechselt von Bank auf Karte), Eintrag
  in der CSV aktualisieren.

---

## SONDERFÄLLE / MEHRERE PDFs PRO BELEG

- **UTA Edenred (Tankkarte):** Die Mail enthält **immer 3 PDFs**, alle werden
  für die Buchhaltung gebraucht (Fahrzeug-Aufschlüsselung). → **Zu EINEM PDF
  zusammenführen** (Rechnung zuerst, dann Aufschlüsselungen), sauber benennen
  (`UTA_Tankkarte_JJJJ-MM.pdf`), Originale behalten, das zusammengeführte PDF an
  Box **Bank** weiterleiten (Lastschrift).
- Allgemein: Gehören mehrere PDFs zu **einem** Beleg → zu einem PDF zusammenführen,
  bevor an DATEV weitergeleitet wird (ein Beleg = ein Dokument).

---

## WORKFLOW

1. **Eingang erfassen** — Rechnung liegt in rechnung@xmedia24.com (oder Scan/Download).
2. **Klassifizieren** — Rechnungssteller in `datev_routing.csv` prüfen → Ziel-Box.
   Offene Zahlung (Rechnungseingang) oder bereits per Lastschrift/Karte bezahlt?
3. **Prüfen** — Betrag, Rechnungssteller, Leistungszeitraum, USt korrekt?
4. **Weiterleiten an DATEV** — an die passende Uploadmail (App oder E-Mail-Link)
   → OWNER-GATE.
5. **Überweisung vorbereiten** (nur offene Posten) — Übersicht Empfänger/IBAN/
   Betrag/Zweck/Fälligkeit → OWNER-GATE, Dirk zahlt selbst.
6. **Zahlung überwachen** — offene Posten als datierte Aufgabe (Wenn-Dann-Pflicht).

---

## x-media event GmbH — Belegweg über Dropbox

Andere Firma, **anderer Weg**: KEINE DATEV-Uploadmail. Belege werden in
**Dropbox-Ordner** einsortiert, auf die der **Steuerberater direkt zugreift**.
Kein Mailversand → Beleg wird **in den passenden Ordner kopiert/verschoben**
(Ablegen/Verschieben = OWNER-GATE).

**Basis-Pfad:** `…/Dropbox/x-media EVENT GmbH/XE Buchhaltung/`
(im Hub angebunden; Routing-Tabelle: `module/buchhaltung/event_routing.csv`)

| Belegart / Zahlweg | Ziel-Ordner |
|---|---|
| Offene Eingangsrechnung (zu zahlen) | `XE offene Eingangsrechnungen` |
| Bezahlte Eingangsrechnung (Überweisung/Lastschrift) | `XE bezahlte Eingangsrechnungen` |
| Bezahlt per Mastercard | `XE bezahlte Eingangsrechnungen/Master` |
| Barbeleg / Kasse | `XE Kassenbelege` |
| Eigene Ausgangsrechnung | `XE offene Ausgangsrechnugnen` (sic — Ordnername mit Tippfehler) |

- **Nach Zahlung:** offene ER von `XE offene Eingangsrechnungen` → `XE bezahlte
  Eingangsrechnungen` verschieben (event-basiert, nach Überweisung).
- **Mail-Eingang event:** sobald `rechnung@xmedia-event.de` / `info@xmedia-event.de`
  bei Strato existieren, in `mail.env` einbinden → dann laufen event-Belege
  automatisch ein (Firma über Empfängeradresse). Bis dahin kommen event-Rechnungen
  über info@ oder werden direkt übergeben.

---

## BELEGE AUS PORTALEN HOLEN (Amazon, Facebook & Co.)

Wiederkehrender Schmerzpunkt: bei Portalen einloggen und Belege herunterladen.

- Ablauf beim ersten Durchgang festlegen (welche Portale, Zeiträume, Zielordner).
- Login/Downloads über Browser-Tools — **Zugangsdaten gibt Dirk aktiv ein**,
  ich speichere keine Passwörter im Hub.

---

## BEWIRTUNGSBELEGE (iPhone-Scan + Zusatzblatt)

Dirk erfasst Bewirtungsbelege unterwegs per iPhone-Kurzbefehl „Bewirtungsbeleg":
Beleg scannen → Angaben diktieren → Mail an **rechnung@**.

**Firma über die Empfängeradresse** (nicht über den Betreff):
- **music** → `rechnung@xmedia24.com` → DATEV
- **event** → `rechnung@xmedia-event.de` → Dropbox *(Postfach noch einzurichten)*

**Betreff:** nur der **Zahlweg** nötig — `bar` oder `EC` (Wortlaut flexibel, z. B.
„Bewirtungsbeleg Bar"). **Der Zahlweg im Betreff ist MASSGEBLICH** — NICHT die
Kartenzeile auf dem Beleg (Dirk zahlt evtl. privat und entnimmt das Geld aus der
Kasse → dann zählt „bar"/Kasse). Nicht gegen den Beleg gegenprüfen.

**Auslesen:** Ort/Datum/Beleg-Summe kommen aus dem Beleg-PDF; Teilnehmer, Anlass
und der maßgebliche Betrag (inkl. Trinkgeld) aus dem Mailtext (auch `inline`-Teil
beachten!).

**Body-Konvention** (der Kurzbefehl schreibt beschriftete Zeilen):
```
Ort: <Gaststätte, Ort>
Datum: <TT.MM.JJJJ>        (fehlt → Mail-Datum)
Betrag: <z. B. 84,50>
Teilnehmer: <Name (Firma); Name (Firma)>
Anlass: <konkreter Anlass>
```

**Ablauf im Hub:**
1. Mail mit Betreff `BEWIRTUNG …` erkennen (in rechnung@ / info@).
2. Angaben aus dem Body + den Scan (PDF/Bild-Anhang) ziehen.
3. `python3 scripts/bewirtung.py --scan <datei> --datum … --ort … --betrag … --zahlweg <bar|ec> --firma <music|event> --teilnehmer … --anlass …`
   → erzeugt **Zusatzblatt + Scan als EIN PDF** in `module/buchhaltung/bewirtung/`.
4. Routing:
   - **music, bar → Kasse** `868708a5-cb99-4ab3-ae70-0c71199e0f8a@uploadmail.datev.de`
   - **music, EC → Bank** `06aa928a-7817-4bcf-a4ef-c2185efe6c35@uploadmail.datev.de`
   - **event → Dropbox** (Zielordner noch zu hinterlegen — bis dahin lokal in `module/buchhaltung/bewirtung/` ablegen und Dirk informieren)
5. Weiterleitung/Ablage **nur nach OWNER-GATE**. Fehlt eine Pflichtangabe (Teilnehmer/Anlass) → bei Dirk nachfragen, nicht raten.

---

## GEMISCHTES POSTFACH info@ — RECHNUNGS-DETEKTOR

info@ enthält Rechnungen gemischt mit Newslettern, Anfragen, GEMA usw. Deshalb
**konservativ** vorgehen mit `scripts/ist_rechnung.py`:

- Merkmal-Scoring im PDF (Rechnungsnummer, USt/MwSt, Netto/Brutto, Gesamtbetrag,
  USt-IdNr, IBAN, Zahlungsziel) + bekannter Absender (`datev_routing.csv`) +
  Ignorier-Liste (`module/buchhaltung/ignorieren.csv`).
- **RECHNUNG** → normal klassifizieren. **GRENZFALL** → Dirk bestätigen lassen,
  dann lernen (Ja → Routing-Tabelle, Nein → Ignorier-Liste). **KEINE** → ignorieren.
- Ein info@-Beleg wird **nie** ohne Bestätigung weitergeleitet, wenn nicht sicher
  RECHNUNG. rechnung@ dagegen offensiv (dediziertes Belegpostfach).

---

## OFFENE PUNKTE

- [ ] **event GmbH:** konkrete Dropbox-Ordnerstruktur + Pfad hinterlegen
- [ ] Ordnerstruktur + Dateinamen-Schema (music)
- [ ] Welche Portale für Beleg-Download (Amazon, Facebook, …)
- [ ] Format der Überweisungs-Übersicht
