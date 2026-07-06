# Deine Betriebsanleitung — so steuerst du den Hub

Hi Dirk! Das hier ist die Bedienungsanleitung für deinen Business-Hub. Kein
Fachchinesisch, versprochen — nur das, was du wissen musst, um loszulegen und
das Ding sicher zu steuern.

---

## Was ist der Hub überhaupt?

Stell ihn dir als dein persönliches **„Super-Gehirn"** in Claude Code vor. Er:

- **denkt mit** — behält Kontakte, Anfragen, Angebote, Fristen und laufende
  Vorgänge im Blick,
- **führt Akten** — für jede Band, jede Venue, jeden Veranstalter legt er eine
  kurze Wegweiser-Notiz an (wo liegt was, was war der letzte Stand),
- **bereitet Mails vor** — schreibt dir Entwürfe, Angebote, Nachfass-Mails,
- **tut aber nichts nach außen ohne dein ausdrückliches JA.**

Der letzte Punkt ist der wichtigste — dazu unten die goldene Regel.

---

## Wie starte ich?

1. Diesen Ordner in **Claude Code** öffnen.
2. Als erste Nachricht einfach **„Hi"** tippen.
3. Beim allerersten Mal führt dich ein kurzer **Onboarding-Dialog** durch ein
   paar Fragen (dein Name, deine Firma, deine Arbeitsbereiche) und füllt den Hub
   damit. Dauert 10–15 Minuten, danach ist er auf dich eingestellt.
4. Ab dann sagst du beim Start einfach „Hi" und der Hub weiß, wo ihr steht.

---

## Das Tannenbaum-Prinzip (Lead-Recherche) — so steuerst du es

Weil du in der Booking-Branche unterwegs bist, ist die **Lead-Recherche** schon
als Gerüst eingebaut. Das Herzstück heißt **Tannenbaum** — weil sich aus einem
Startpunkt immer neue Äste ergeben. So läuft es:

1. **Du gibst den Startpunkt vor.** Zum Beispiel:
   *„Starte einen Tannenbaum ausgehend von [Künstler oder Venue]."*
2. **Der Hub sammelt autonom.** Er folgt der Kette:
   **Künstler → Tourdaten → Venues → Veranstalter → Impressum → Lead.**
   Aus jedem Ast wachsen neue — daher „Tannenbaum". Das läuft selbstständig,
   du musst nicht danebensitzen.
3. **Sammelkorb.** Alle gefundenen Leads landen erst in einer Sammelliste
   (`module/akquise/sammelliste.csv`) — noch nichts geht raus, alles nur geparkt.
4. **Veredelung.** Der Hub putzt den Sammelkorb: **Impressum-Check** (echte
   Kontaktdaten?), **Dubletten-Prüfung** gegen deine **Bestandsliste** (kennen
   wir den schon?), Qualitätsfilter (passt die Zielgruppe, ist eine Mail da?).
5. **Kontaktformulare.** Wo keine Mail-Adresse existiert, aber ein
   Kontaktformular auf der Website — trägt der Hub das automatisch aus.
6. **Freigabe (Gate).** Am Ende legt er dir **alles gebündelt vor**: wie viele
   Leads, an wen, mit welchem Betreff, plus eine Beispiel-Mail. **Erst dein JA
   verschickt irgendwas.**
7. **Bestandsliste.** Nach dem Versand wandern die Leads aus dem Sammelkorb in
   deine Bestandsliste — damit du sie beim nächsten Tannenbaum nicht doppelt
   anschreibst.
8. **Bounces.** Kommt eine Mail als unzustellbar zurück, erkennt der Hub das
   automatisch, notiert es in der Akte und recherchiert eine neue Adresse nach.

Kurz: **Du sagst wo's losgeht — der Hub macht die Fleißarbeit — du gibst frei.**

---

## Steuer-Beispiele (einfach so tippen)

| Was du willst | Was du tippst |
|---|---|
| Neue Lead-Recherche starten | „Starte einen Tannenbaum ab [Künstler/Venue]." |
| Nachsehen, was gesammelt wurde | „Zeig mir den Sammelkorb." |
| Sammelkorb putzen lassen | „Veredle die Sammelliste." |
| Versand vorbereiten (→ Gate) | „Bereite den Versand vor." |
| Unzustellbare Mails prüfen | „Checke Bounces." |
| Überblick bekommen | „Report." |

Du musst nichts auswendig lernen — sag es in deinen eigenen Worten, der Hub
versteht die Absicht.

---

## Die goldene Sicherheits-Regel

**Alles, was nach außen geht** — jede Mail, jedes Kontaktformular, jeder Brief —
zeigt dir der Hub **vorher komplett** und wartet auf dein ausdrückliches
**„ja" / „senden" / „raus damit"**. Das nennen wir das **OWNER-GATE**.

- Ein „ja" deckt immer nur **die eine** Sache, die gerade auf dem Tisch liegt.
- Stille, ein Nicken oder „passt schon" reichen **nicht** — es braucht ein klares
  Wort.
- **Kein Selbstläufer.** Der Hub verschickt nie etwas „nebenbei".

Das ist kein Misstrauen dir gegenüber — es ist dein Sicherheitsnetz, damit nie
aus Versehen etwas Falsches oder etwas Halbfertiges rausgeht.

---

## Es gehört dir

Der ganze Hub ist **deiner**. Alle Regeln liegen als einfache Textdateien in
`.claude/rules/` und sind **jederzeit änderbar**:

- **Regel ändern:** Sag einfach „ab jetzt immer …" oder „bei Thema X nie …" —
  der Hub schreibt es in die passende Regel-Datei, und der nächste Chat hält
  sich dran.
- **Modul anlegen:** Wiederholt sich ein Thema? „Leg mir dafür ein eigenes
  Modul an." — fertig.
- **Modul abschaffen:** „Brauch ich nicht mehr." — weg damit.

**Nur die 5 absoluten Sicherheits-Regeln bleiben** (keine Mail ohne dein Ja,
kein Löschen ohne Backup, keine Beträge/Gagen ohne dich, keine Zahlungen ohne
dich, bei Unsicherheit fragen). Die sind als **Schutz** da, nicht als Schikane —
alles andere ist Verhandlungssache zwischen dir und dem Hub.

---

Viel Spaß damit — und wenn was unklar ist: einfach den Hub fragen. Er erklärt
sich gern selbst.
