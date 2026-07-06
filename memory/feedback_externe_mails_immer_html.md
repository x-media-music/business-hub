---
name: Externe Mails immer HTML mit Struktur
description: Externe Geschäfts-Mails werden NIE als Plaintext gesendet — immer HTML mit Absätzen, Listen, fett/Hervorhebungen. Plaintext flacht beim Empfänger zu unlesbarem Fließtext ab.
type: feedback
---
**Regel:** Jede externe E-Mail (Kunde, Veranstalter, Hotel, Lieferant, Behörde, Anwalt) wird **als HTML** gesendet — mit echten Absätzen (`<p>`), Listen (`<ul>/<li>`), Hervorhebungen (`<strong>`) und Tabellen (`<table>`), wo der Inhalt es verlangt.

**Konkret bei `scripts/send_email.py`:**
- `--format html` setzen (nicht `text`)
- Body als HTML-Datei vorbereiten mit echten Tags, nicht nur Zeilenumbrüchen
- Mehrere Absätze → `<p>...</p>` blocks, NIE einfach `\n\n`
- Listen → `<ul><li>...</li></ul>`, NIE Bindestriche oder Sternchen am Zeilenanfang
- Hervorhebungen → `<strong>` (oder `<b>`), NIE Asterisks oder Großschrift
- Tabellen → `<table><tr><td>`, NIE Pipe-Zeichen `|`
- Lange Werte (Adressen, Beträge) → eigener Absatz mit visueller Trennung, evtl. eingerückt via `<blockquote>`

**Why:**
Plaintext-Bodies werden im Empfänger-Client oft zu einem einzigen Fließtext-Block ohne Absätze, ohne Listen, ohne Lesbarkeit — unübersichtlich und unprofessionell. Selbst wenn die Plaintext-Quelle Zeilenumbrüche hat: Viele Mail-Clients (Outlook, Web-Mailer, mobile Clients) ignorieren oder kollabieren `\n` aus Plaintext-Mails. Nur HTML garantiert Struktur.

**How to apply:**
- Default für **send_email.py** bei externen Empfängern: `--format html`
- Body-Datei mit HTML-Tags vorbereiten (`<p>`, `<ul>`, `<li>`, `<strong>`, `<table>`, `<blockquote>` etc.)
- Vor OWNER-GATE: kurz prüfen ob Listen/Tabellen im Entwurf vorkommen — wenn ja: HTML zwingend
- Plaintext OK NUR für: rein interne Kurzhinweise — aber selbst dort lieber HTML, schadet nicht
- Bei Vorlagen-Templates (`vorlagen/email/*.md`): markdown-strukturierten Inhalt zu HTML konvertieren, nicht 1:1 als Plain rausgeben

**Korrektur-Hinweis bei nachträglich erkanntem Plaintext-Verlust:**
Den Owner informieren, anbieten eine Korrektur-Mail in HTML hinterherzusenden mit Hinweis "die vorherige Mail war schwer lesbar, hier in besserer Darstellung".
