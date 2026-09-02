# Nachzutragen in `.claude/rules/03_buchhaltung.md`

Cowork-Cloud-Sessions dürfen nicht in `.claude/` schreiben. Diesen Block bitte in einer
Mac-Session (oder von Hand) vor dem Abschnitt „GEMISCHTES POSTFACH info@" einfügen —
danach diese Datei löschen.

---

## BELEGMAILS OHNE PDF-ANHANG (Apple, PayPal & Co., seit 20.08.2026)

Viele wiederkehrende Belege kommen nur als HTML-Mail. Der Hub erzeugt daraus selbst
ein PDF (`scripts/bh_html2pdf.py`, im Ingest verdrahtet) und legt den Beleg wie jeden
anderen als **Wartend** in die App — Freigabe bleibt bei Dirk.

- Zielbox aus dem Zahlweg: **Mastercard → Kreditkarte Master** · **PayPal / Lastschrift /
  EC → Bank** · sonst **Rechnungseingang**. `datev_routing.csv` hat Vorrang.
- Fest eingebaut: **Apple, PayPal**. Weitere Absender ohne Code ergänzen in
  `module/buchhaltung/html_belege.csv` (Absender-Regex; Betreff-Regex; Zielbox; Typ; Notiz).
- Greift nur mit Absender-Regel **und** erkanntem Betrag → keine Fehlalarme aus Newslettern.
- Das PDF enthält Kopfdaten, den vollständigen Mailtext und den Hinweis, dass es aus einer
  E-Mail erzeugt wurde; die Originalmail bleibt im Postfach (Regel „nicht vorab archivieren").
- Ältere Mails nachziehen: `python3 scripts/bh_ingest.py --box info --from-uid <UID> --dry-run`.
