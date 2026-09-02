# Modul Darlehen — Darlehen an Musiker/Dienstleister

Führt Darlehenskonten als Staffelrechnung mit taggenauen Zinsen und erzeugt daraus ein
finanzamtfähiges Datenblatt (PDF) mit vollständigem Zins-/Tilgungsverlauf.

**Angelegt:** 31.08.2026 (Anlass: Darlehen an Janis Herb, 4.000 € vom 01.04.2026)

---

## AKTIVE DARLEHEN

| Darlehensnehmer | Slug | Geber | Betrag | Ausgereicht | Zins | Stand 31.08.2026 |
|---|---|---|---|---|---|---|
| Janis Herb | `janis_herb` | x-media music GmbH | 4.000,00 € | 01.04.2026 | 3,0 % p. a. | **2.037,82 €** offen |

---

## DATEIEN JE DARLEHEN

| Datei | Inhalt |
|---|---|
| `stammdaten_<slug>.csv` | Vertragsdaten: Geber, Nehmer, Betrag, Zinssatz, Methode, Sicherheiten |
| `darlehen_<slug>.csv` | Bewegungen: `Datum;Vorgang;Betrag;Beleg;Notiz` — **die führende Quelle** |

Vorgänge: `AUSZAHLUNG` · `TILGUNG` · `ZINSZAHLUNG` · `ERHOEHUNG`
Format wie im Hub üblich: Semikolon-getrennt, UTF-8, Datum TT.MM.JJJJ, Beträge mit Komma.

---

## BEDIENUNG

```bash
# Stand ansehen
python3 scripts/darlehen.py janis_herb --status

# Neue Tilgung buchen (Dublettenschutz eingebaut)
python3 scripts/darlehen.py janis_herb --buchen \
    --datum 30.09.2026 --vorgang TILGUNG --betrag 200 \
    --beleg "RG 09/2026" --notiz "Verrechnung mit Gagenrechnung September"

# Datenblatt + Verlauf als PDF (landet in reports/ + Ansicht Dokumente/hub_Owner/)
python3 scripts/darlehen.py janis_herb --pdf
python3 scripts/darlehen.py janis_herb --pdf --stichtag 31.12.2026   # mit Zinsabgrenzung
```

---

## RECHENWEG (bewusst festgelegt, nicht ändern ohne Rücksprache)

Staffelmethode, taggenau **act/365**:

```
Zins Abschnitt = Restschuld × Zinssatz × Ist-Tage / 365      (auf 2 Stellen gerundet)
neue Restschuld = alte Restschuld + Zins − Tilgung
```

Der Zins wird der Restschuld **zugeschlagen** (Kapitalisierung) — so hat Dirk es angelegt,
so wird es fortgeführt. Umstellung auf § 367 BGB (erst Zinsen, dann Kapital) wäre möglich,
ist aber bewusst nicht gewählt.

---

## WORKFLOW BEI JEDER TILGUNG (Pflicht)

Janis meldet Tilgungen **in seinen Rechnungen** („bitte 150 € als Tilgung abziehen"). Deshalb:

1. **Beleg-Check / Briefing erkennt** eine Rechnung von Janis Herb mit Tilgungshinweis.
2. Betrag, Rechnungsbezug und Datum notieren. **Buchungsdatum = Tag der Zahlung**,
   nicht das Rechnungsdatum — vorher steht die Tilgung nur als „VORGEMERKT" in der Notiz.
3. Nach der Überweisung: `--buchen` ausführen, Notiz von „VORGEMERKT" bereinigen.
4. Gegenprobe: Rechnungsbetrag − Tilgung = tatsächlich überwiesener Betrag.
5. Auf der Zahlungs-Aufgabe in `module/aufgaben/aufgaben.csv` den Tilgungsbetrag vermerken,
   damit bei der Überweisung nicht der volle Rechnungsbetrag rausgeht.

**Buchhalterisch:** Die Eingangsrechnung wird in **voller Höhe** als Aufwand erfasst und
normal an DATEV übergeben (Beleg-Check). Nur die *Zahlung* ist gekürzt; die Differenz
mindert die Darlehensforderung. Janis ist §19-Kleinunternehmer → keine Vorsteuerfrage.

---

## JAHRESABSCHLUSS

Zum 31.12. jedes Jahres:

- `--pdf --stichtag 31.12.JJJJ` erzeugen → weist die Zinsabgrenzung bis Jahresende aus.
- PDF zum Jahresabschluss an die Steuerberatung (Storm) geben.
- Aufgabe dafür liegt in `module/aufgaben/aufgaben.csv` (Kategorie „Frist").

---

## OFFENE PUNKTE

- [ ] **Darlehensvertrag im Hub ablegen** (liegt laut Dirk vor) → `module/darlehen/vertrag_janis_herb.pdf`
- [ ] Aus dem Vertrag nachtragen: Vertragsdatum + vereinbarte Zinsmethode (Endfälligkeit und Sicherheiten sind geklärt: keine feste Laufzeit, keine dinglichen Sicherheiten — steht so im Datenblatt)
- [ ] Rechnungsbezug für die Tilgung vom 30.07.2026 (600 €) nachtragen
- [ ] Prüfen, ob der Zinssatz von 3 % dem Fremdvergleich standhält (Steuerberatung)
