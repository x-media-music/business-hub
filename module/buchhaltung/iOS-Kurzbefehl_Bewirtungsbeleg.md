# iOS-Kurzbefehl „Bewirtungsbeleg" — Bauanleitung

Ziel: **ein Tipp** → Zahlweg & Firma wählen → Ort/Betrag/Teilnehmer/Anlass
**einsprechen** → Beleg **scannen** → fertig adressierte Mail an rechnung@.

App: **Kurzbefehle** (Shortcuts, auf jedem iPhone vorinstalliert).
Neuen Kurzbefehl anlegen: **+** oben rechts → Namen „Bewirtungsbeleg" geben.
Folgende Aktionen der Reihe nach hinzufügen (Suchfeld unten):

1. **Aus Menü wählen** („Choose from Menu")
   - Titel: „Zahlweg?" · Einträge: **Bar**, **EC**
   - In jedem Zweig gleich die nächste Aktion setzen — oder einfacher: das
     Ergebnis in eine Variable „Zahlweg" sichern (bei jedem Menüpunkt Aktion
     **Variable festlegen → Zahlweg** = `bar` bzw. `EC`).

2. **Aus Menü wählen** — Titel „Firma?" · Einträge **music**, **event**
   → Variable **Firma** = `music` bzw. `event`.

3. **Nach Eingabe fragen** („Ask for Input"), Typ *Text*
   - Frage: „Ort der Bewirtung?" → Variable **Ort**
   - (Diktat: beim Tippen die **Mikrofon-Taste** der Tastatur nutzen)

4. **Nach Eingabe fragen**, Typ *Text* — „Betrag in €?" → Variable **Betrag**

5. **Nach Eingabe fragen**, Typ *Text* — „Teilnehmer? (mit ; trennen)" → **Teilnehmer**

6. **Nach Eingabe fragen**, Typ *Text* — „Anlass der Bewirtung?" → **Anlass**

7. **Aktuelles Datum** → **Datum formatieren** (Format „TT.MM.JJJJ") → Variable **Datum**

8. **Dokumente scannen** („Scan Documents") — Kamera scannt den Beleg → ergibt ein **PDF**.

9. **Text** (Aktion „Text") — trage exakt dieses Muster ein und setze die Variablen ein:
   ```
   Ort: [Ort]
   Datum: [Datum]
   Betrag: [Betrag]
   Teilnehmer: [Teilnehmer]
   Anlass: [Anlass]
   ```

10. **E-Mail senden** („Send Email")
    - **An:** `rechnung@xmedia24.com`
    - **Betreff:** `BEWIRTUNG ` + Variable **Zahlweg** + ` ` + Variable **Firma**
      (ergibt z. B. `BEWIRTUNG bar music`)
    - **Textkörper:** die **Text**-Ausgabe aus Schritt 9
    - **Anhang:** das **gescannte PDF** aus Schritt 8
    - „Vorschau anzeigen" **an** lassen → du siehst die Mail und tippst nur noch **Senden**.

Fertig. Kurzbefehl aufs Home-Bildschirm legen (Teilen → „Zum Home-Bildschirm")
für den Ein-Tipp-Start.

---

## Was danach im Hub passiert (automatisch)

Die Mail landet in rechnung@ mit Betreff `BEWIRTUNG <bar|EC> <music|event>`.
Der Hub (täglicher Check oder auf Zuruf):

1. liest Body + Scan,
2. erzeugt das **Bewirtungsbeleg-Zusatzblatt** und **führt es mit dem Scan zu
   einem PDF zusammen**,
3. legt es dir als **Gate** vor → auf „Ja":
   - **bar → DATEV-Box Kasse**, **EC → DATEV-Box Bank** (music)
   - **event → Dropbox** (Zielordner wird noch hinterlegt).

Fehlt eine Pflichtangabe (Teilnehmer/Anlass), fragt der Hub nach — er rät nicht.

---

## Ohne Kurzbefehl (manuelle Alternative)

Beleg mit **Notizen → Dokument scannen** aufnehmen, per **Teilen → Mail** an
rechnung@xmedia24.com senden, Betreff `BEWIRTUNG bar music` (o. ä.), und die
fünf Zeilen (Ort/Datum/Betrag/Teilnehmer/Anlass) in den Mailtext **diktieren**.
