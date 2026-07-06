---
name: Offizielle Schreiben immer professionell und aufgeräumt
description: Alle externen Schreiben (Widersprüche, Briefe, Verträge, Anwaltskorrespondenz, Behörden) müssen professionell aussehen — DIN-5008-Layout, klare Struktur, Weißraum, saubere Typografie. Nicht nur Inhalt zählt, auch Außenwirkung.
type: feedback
---
**Regel:** Wenn ich ein externes Schreiben als Word/PDF baue, muss das optisch einem professionellen Geschäftsbrief entsprechen. Inhalt allein reicht nicht — das Layout prägt die Wahrnehmung des Empfängers.

**Why:** Ein textlastig gesetzter Brief ohne Struktur signalisiert Amateur, auch wenn die Argumentation gut ist. Ein unübersichtliches Layout stresst beim Lesen und untergräbt die Glaubwürdigkeit. Externe Schreiben müssen immer professionell und aufgeräumt aussehen.

**How to apply:**

### DIN-5008-Briefkopf
- **Absender oben klein in Grau** (8,5pt, #555)
- **Empfänger-Feld** mit ausreichendem Abstand (ca. 18pt nach Absender)
- **Versandart links** (kursiv grau) + **Datum rechtsbündig** auf derselben Zeile via Tabstop
- **Betreff fett**, 12pt, mit Untertitel-Zeile(n) 10,5pt

### Typografie
- **Schrift:** Calibri oder Arial 11pt (Fließtext), 10,5pt für Zitate/Untertitel, 9pt für Fußzeile
- **Zeilenabstand:** 1,15
- **Abstand nach Absätzen:** 6pt (Standard), 12pt vor/nach Abschnitten
- **Seitenränder:** 2,5cm links, 2,0cm oben/rechts/unten
- **Farben:** Hauptfarbe Schwarz; Grautöne #444–#555 für sekundäre Infos; Akzentfarbe nur wenn sinnvoll

### Struktur
- **Nummerierte Abschnitte fett** mit Abstand davor (14pt) + keep_with_next
- **Zitate eingerückt** (links 1cm, rechts 1cm, kursiv, graue Schrift), abgesetzt durch 4pt/12pt Abstände
- **Kernaussagen fett** hervorheben (aber sparsam)
- **Fazit-Sätze** in eigenem Absatz, fett

### Tabellen
- **Header-Zeile farbig** (z.B. dunkelgrau #4A5568), Text weiß
- **Zebra-Zeilen** (jede zweite Zeile #F5F5F5)
- **Zellränder hellgrau** (#CCCCCC), nicht schwarz
- **Beträge rechtsbündig**, Label linksbündig
- **Summen-Zeile** farblich abgesetzt (z.B. #E8F0FE)
- **Spaltenbreiten explizit** setzen

### Fußzeile
- **Seitenzahl mittig** („Seite X von Y"), 9pt grau
- Bei mehrseitigen Schreiben Pflicht

### Grußformel + Unterschrift
- Grußformel mit ~24pt Abstand nach dem letzten Textabsatz
- **3–4 Leerzeilen (48pt) Platz für Unterschrift**
- Name als einfache Zeile, keine aufgeblasene Signatur

### Anlagen-Block
- „Anlagen" als kleine fette Überschrift (10,5pt)
- Auflistung 10,5pt in Grau #444
- Abstand nach oben ~12pt

### Technische Umsetzung
- Scripts bauen Word + PDF gleichzeitig, über `python-docx` + `docx2pdf`
- Anlagen mit `pypdf` zu einer Master-PDF mergen
- Bilder (JPG/PNG) erst zu PDF konvertieren, dann mergen

### Gilt für
- Widersprüche, Einsprüche, Anwaltskorrespondenz
- Verträge, Zahlungsversprechen, offizielle Angebote
- Behördenschreiben (Finanzamt, Gerichte, Gewerbeaufsicht)
- Professionelle Geschäftskorrespondenz ohne spezifischen Marken-Briefkopf

### NICHT zwingend für
- Interne Mails
- Kurznachrichten
- Kurze Bestätigungs-Mails
- Booking-/Marken-Kommunikation mit eigenem Briefstil und eigener Signatur

**Bei Unsicherheit:** Das Ergebnis dem Owner **vor** dem Versand zeigen, nicht erst danach. Er kann das Layout kritisieren, bevor es raus geht.
