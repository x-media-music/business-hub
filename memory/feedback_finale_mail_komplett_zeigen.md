---
name: Vor jeder Freigabe finale Mail komplett zeigen (Body + Signatur)
description: Der Owner will den 1:1-Wortlaut sehen, der tatsächlich rausgeht — inklusive der vom Script angehängten Signatur. Kein Body-only mehr.
type: feedback
---
**Regel:** Bei JEDER externen Email muss vor dem OWNER-GATE die **vollständige finale Mail** im Chat erscheinen — Body **plus** der vom `send_email.py` automatisch angehängten Signatur (Signatur-Block + Kontext-Kopf + Adresse + Website). Der Owner will den Wortlaut sehen, der beim Empfänger ankommt — nicht nur den Body, auf den später eine Signatur draufgepatcht wird.

**Why:** Wenn nur der Body gezeigt wird und das Script die Signatur automatisch anhängt, fallen falsche Website-Domain, falscher Kopf oder falscher Absender-Block erst auf, wenn die Mail schon raus ist. Mit kompletter Vorschau ist das sofort sichtbar.

**How to apply:**
1. Body schreiben — wie bisher
2. Anhängende Signatur **vorab manuell zusammenbauen** und 1:1 unter den Body kleben (siehe die Signatur-Builder in `scripts/send_email.py`)
3. Komplette Mail im Chat in einem Block zeigen
4. Gate: OWNER-GATE mit Hinweis „Diese Version geht 1:1 raus" und Hash der finalen Mail
5. Bei [JA]: senden, Hash über `--gate-hash` mitgeben damit das Script bei Abweichung blockt
6. Bei [ÄNDERN]: neue komplette Mail zeigen, neuer Hash, neues Gate

**Was die Vorschau zwingend abdeckt:**
- Body 1:1 wie er rausgeht (inkl. Anrede, ggf. Body-Intro bei Erstkontakt)
- Grußformel (z.B. „Mit freundlichen Grüßen")
- Sender-Zeile + ggf. Sekretariats-Vermerk
- Kopf-Zeile (je nach Geschäftsbereich)
- Vollständige Adress- und Kontaktdaten
- **Website-URL** (häufigste Falle bei mehreren Domains/Geschäftsbereichen)
