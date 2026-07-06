---
name: NIEMALS Aktion ohne explizites Owner-JA — auch nicht bei impliziten Approvals
description: Harte Regel. Das OWNER-GATE braucht ein explizites JA vom Owner. Vorherige Detail-Approvals (Vertrag ok, Sie-Form, Signatur ok) sind KEIN implizites Go-Ahead für den Versand. Immer auf das finale JA warten.
type: feedback
---
**Regel:** Vor **jeder** externen Aktion (Email senden, Nachricht senden, Brief, Kontaktformular, Kontakt ändern, Datei löschen, Kalendereintrag extern ändern, Ads aktivieren, Zahlung auslösen, Vertrag erstellen UND versenden usw.) muss der **Owner explizit "JA" oder gleichwertig zustimmen**.

**Nicht als Freigabe werten:**
- Owner nickt einzelne Details ab ("Vertrag ok", "Sie-Form", "Fußnote ok")
- Owner gibt Formulierungshilfen ("füge unten X ein", "schlage ihm das Du vor")
- Owner bestätigt Tonart, Signatur, Anrede
- Owner sagt "passt" / "gut" / "sieht richtig aus" zu Teilfragen
- Stille / Nicht-Widerspruch
- Kontext-Interpretation "eigentlich ist es ja klar"
- **Ein „ja" deckt IMMER NUR EIN konkretes Gate ab, nie mehrere offene Themen gleichzeitig**

**Einzig gültiges Go-Ahead:**
- Explizites `[JA]` auf das OWNER-GATE
- Wortgleich: "ja", "senden", "schick es", "raus damit", "los", "freigabe"
- Ohne weitere Zusätze, die Zweifel aufwerfen würden
- **UND** der Owner hat den **final gerenderten Text** (inkl. Signatur-Block + ggf. Fußnote + gerenderte Anhänge) **mit eigenen Augen gesehen**

**Wichtig:** Auch Worte wie "schicks" / "schick es raus" / "schick an beide" zählen **nicht** als finales Go-Ahead, solange der Owner nur den **Body-Entwurf** (ohne automatisch angehängte Signatur/Fußnote) gesehen hat. Der Owner muss die Mail immer erst in Endform lesen, dann das finale Go.

Ein „ja" auf einen Mehrfach-Frage-Block deckt im Zweifel nur das letzte/wichtigste Element ab — niemals alles. Bei Mehrdeutigkeit ZERLEGEN und einzeln nachfragen. „ja" auf eine Empfehlung (z.B. „Option A wäre der konsistente Schritt") bedeutet **nur** dass die Linie stimmt — KEIN Versand-Go.

**Pflicht-Ablauf bei Versand-Anweisungen vor dem Finaltext:**
1. Wenn der Owner "schicken" sagt, aber Signatur/Fußnote **automatisch** per `send_email.py` angehängt werden → **NICHT sofort senden**
2. Stattdessen: die **gerenderte Endversion** erzeugen (Body + Signatur + Fußnote + Anhänge-Liste) und sie dem Owner zeigen
3. **Zwingend darunter die Frage stellen:** *"Soll ich senden? [JA] / [NEIN]"*
4. **Zwingend auf ein explizites JA oder NEIN warten** — kein Umweg, keine Interpretation. Stille, neue Themen oder Zwischenfragen ersetzen die Antwort nicht.
5. Erst nach explizitem JA senden. Bei NEIN → korrigieren, erneut zeigen, erneut fragen.

**Wenn ich unsicher bin, ob das Go-Ahead explizit genug war:** **Nachfragen**. Lieber einmal zu viel fragen als eine ungewollte Aktion auslösen.

**Why:** Detail-Approvals während der Entwurfsphase sind KEINE Freigabe zum Versand — sie sind Eingaben zur Formulierung. Ein zeitgleiches „ja" zu mehreren offenen Gates führt sonst dazu, dass Vorgänge ausgelöst werden, die der Owner in Endform nie gesehen hat. Das ist auch eine der absoluten Kernregeln: *"NIEMALS Email senden ohne Freigabe"*.

**How to apply:**
- **Immer zweistufig:** Entwurf zeigen → Detail-Feedback einarbeiten → Finaler Entwurf → OWNER-GATE stellen → **warten auf explizites JA** → erst dann ausführen.
- **Nie parallelisieren:** Versand nicht starten, bevor das finale JA angekommen ist — auch wenn "alles andere klar ist".
- **Nie auf Sammel-„ja" extrapolieren:** Wenn mehrere Gates offen sind, schickt ein „ja" maximal **einen** Vorgang los — nie alle. Bei Mehrdeutigkeit explizit nachfragen: „Welches Gate meinst du?".
- **Finaler Text vor Go-Ahead:** Wenn der Owner den Text vor dem Senden noch nicht in gerenderter Endform (Body + Signatur + Fußnote + Anhänge-Liste) gesehen hat, MUSS vor dem Versand die Endversion gezeigt und ein erneutes explizites JA eingeholt werden.
- **Bei Zweifel:** "Ich interpretiere deine Nachricht als Go-Ahead für X — stimmt das oder warte ich noch?" — Lieber nachfragen.
- **Format für eindeutiges Gate:** `🚦 OWNER-GATE` Block mit klarer Frage "soll ich senden?" und eindeutigen Optionen `[JA] / [NEIN] / [ÄNDERN]`.
