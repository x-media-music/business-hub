# Darlehen Janis Herb

**Typ:** Thema / Buchhaltung
**Zuletzt_gesynct:** 2026-08-31 09:55

## Das Wichtigste

- **x-media music GmbH** hat Janis Herb (Schlagzeuger, janis.herb@googlemail.com) am
  **01.04.2026 ein Darlehen über 4.000,00 €** ausgereicht, **3 % Zinsen p. a.**
- Getilgt wird **unregelmäßig durch Verrechnung mit seinen Gagenrechnungen** — Janis meldet
  von sich aus in der Rechnung, wenn er tilgen kann („bitte 150 € als Tilgung abziehen").
- **Stand 31.08.2026:** 2.000,00 € getilgt, 37,82 € Zinsen aufgelaufen, **Restschuld 2.037,82 €**.
- Geführt wird das Konto im Hub: `module/darlehen/darlehen_janis_herb.csv`,
  Auswertung + PDF über `python3 scripts/darlehen.py janis_herb --status | --pdf`.
  Modul-Beschreibung: `module/darlehen/README.md`

## Prüfung von Dirks Excel-Tabelle (31.08.2026)

Dirks Aufbau (Staffelrechnung, Zins auf Restschuld, Zins wird zugeschlagen) ist **richtig**.
Drei Fehler gefunden:

| Fehler | Detail |
|---|---|
| Tageszahlen zu niedrig | 01.04.→11.05. = **40** Tage (eingetragen 30) · 11.05.→31.05. = **20** (eingetragen 14) · 30.07.→31.08. = **32** (eingetragen 31) |
| Ursache | Spalte „Tage" war **von Hand** gefüllt statt aus den Datumsfeldern gerechnet |
| Jahreszahl-Tippfehler | Zeile 4 stand auf **30.07.3036** statt 30.07.2026 |

Wirkung: 32,73 € statt 37,82 € Zinsen → **5,09 € zu wenig**, Restschuld war um denselben
Betrag zu niedrig (2.032,73 € statt 2.037,82 €).

Korrigierte Fassung mit automatischer Tagesberechnung:
`module/darlehen/Darlehen_Janis_Herb_2026_korrigiert.xlsx`

## Steuerliche Einordnung

- Forderung + Zinsertrag gehören in die **x-media music GmbH** (Darlehensgeber).
- Eingangsrechnungen von Janis werden **in voller Höhe** als Aufwand gebucht und normal an
  DATEV übergeben; nur die Auszahlung ist um die Tilgung gekürzt (Aufrechnung).
  Janis ist **§19-Kleinunternehmer** → keine Vorsteuerthematik.
- **Keine feste Laufzeit, keine Sicherheiten** (Dirk, 31.08.2026). Ohne Laufzeitvereinbarung
  greift § 488 Abs. 3 BGB: Kündigung mit drei Monaten Frist. Sicherheit ist faktisch die
  laufende Geschäftsbeziehung — Janis spielt fortlaufend, die Tilgung läuft über seine Gagen.
  So steht es jetzt auch im Datenblatt (nicht mehr „OFFEN").
- Für den Fremdvergleich beim Finanzamt braucht es den **schriftlichen Darlehensvertrag** —
  liegt laut Dirk vor, ist aber noch nicht im Hub abgelegt.
- Einordnung: Janis ist **fremder Dritter** (kein Gesellschafter, kein Angehöriger) — der
  strenge Fremdvergleichsmaßstab für Gesellschafter-/Angehörigendarlehen greift hier nicht.
  Ein unbesichertes Darlehen an einen Stammmusiker ist plausibel. Bilanziell durch das laufende
  Tilgungstempo faktisch kurzfristig → Einordnung entscheidet die Steuerberatung.
- Zum 31.12. Zinsabgrenzung erzeugen und der Steuerberatung Storm mitgeben.

## Verlauf

| Datum | Wer | Was |
|---|---|---|
| 01.04.2026 | Dirk | Darlehen 4.000 € ausgereicht, 3 % p. a. |
| 11.05.2026 | Janis | 800 € getilgt (Verrechnung RG 04/2026) |
| 31.05.2026 | Janis | 450 € getilgt (Verrechnung RG 05/2026) |
| 30.07.2026 | Janis | 600 € getilgt (Rechnungsbezug noch nachzutragen) |
| 30.08.2026 | Janis | 2. August-Rechnung, bittet um Abzug von 150 € Tilgung (rechnung@ UID 637) |
| 31.08.2026 | Hub | Excel geprüft (3 Fehler), Modul `module/darlehen/` angelegt, Datenblatt-PDF erzeugt |

## Offen

- [ ] Darlehensvertrag ablegen unter `module/darlehen/vertrag_janis_herb.pdf`, dann
      Vertragsdatum in `stammdaten_janis_herb.csv` nachtragen
      (Endfälligkeit + Sicherheiten sind seit 31.08.2026 geklärt: keine / keine)
- [ ] Rechnungsbezug zur Tilgung 30.07.2026 (600 €) ergänzen
- [ ] Tilgung 150 € nach der Überweisung auf das tatsächliche Zahldatum korrigieren
