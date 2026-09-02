#!/usr/bin/env python3
"""
bh_html2pdf.py — Belege aus E-Mails OHNE PDF-Anhang erzeugen.

Viele wiederkehrende Belege kommen nur als HTML-Mail (Apple/iCloud, PayPal-Belege,
Google, Adobe, Hostinger ...). Der Ingest konnte sie bisher nicht erfassen, weil er
auf PDF-Anhaenge angewiesen war. Dieses Modul rendert solche Mails in ein sauberes,
text-durchsuchbares PDF (DATEV-tauglich) und liefert die Belegdaten (Betrag,
Belegnummer, Datum, Zahlweg -> Zielbox) gleich mit.

Bewusst OHNE externe Abhaengigkeiten (nur Standardbibliothek), damit es sowohl in
der Cowork-Sandbox als auch nativ auf dem Mac laeuft. Der PDF-Writer ist minimal,
schreibt aber echte Textobjekte -> pdfplumber/DATEV koennen den Text lesen.

Erkennung ist KONSERVATIV: nur wenn eine Absender-Regel greift UND ein Betrag
gefunden wird, gilt die Mail als Beleg. Alles andere wird ignoriert.

Regeln erweitern:
  - eingebaut: Apple, PayPal (siehe REGELN)
  - zusaetzlich lernbar ueber module/buchhaltung/html_belege.csv
    Spalten: Absender_Muster;Betreff_Muster;Zielbox;Typ;Notiz   (Semikolon, UTF-8)
    Beispiel: adobe.com;rechnung|invoice;kreditkarte_master;eingangsrechnung;Creative Cloud

Aufruf zum Testen:
  python3 scripts/bh_html2pdf.py --demo            # Beispiel-PDF erzeugen
"""
from __future__ import annotations
import re, csv, html as _html, hashlib
from pathlib import Path
from datetime import datetime

HUB = Path(__file__).resolve().parent.parent
REGEL_CSV = HUB / "module" / "buchhaltung" / "html_belege.csv"

# ---------------------------------------------------------------- PDF-Writer --

_PAGE_W, _PAGE_H = 595.28, 841.89          # A4
_MARGIN_X, _MARGIN_TOP, _MARGIN_BOT = 52, 62, 52
_FONT, _FONT_B = "F1", "F2"


def _esc(s: str) -> str:
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def _enc(s: str) -> bytes:
    """cp1252/WinAnsi — deckt Umlaute und € ab; Unbekanntes wird ersetzt."""
    repl = {"–": "-", "—": "-", "’": "'", "‘": "'",
            "“": '"', "”": '"', " ": " ", "•": "-",
            "‹": "<", "›": ">", "…": "...", "‑": "-"}
    for a, b in repl.items():
        s = s.replace(a, b)
    return s.encode("cp1252", "replace")


def _wrap(text: str, width: int) -> list[str]:
    out = []
    for para in text.split("\n"):
        para = para.rstrip()
        if not para:
            out.append("")
            continue
        line = ""
        for word in para.split(" "):
            while len(word) > width:                    # ueberlange Tokens hart brechen
                if line:
                    out.append(line); line = ""
                out.append(word[:width]); word = word[width:]
            if not line:
                line = word
            elif len(line) + 1 + len(word) <= width:
                line += " " + word
            else:
                out.append(line); line = word
        out.append(line)
    return out


class _Pdf:
    """Minimaler, aber gueltiger PDF-Writer (Helvetica, mehrseitig)."""

    def __init__(self, size=9.0, leading=12.0):
        self.size, self.leading = size, leading
        self.pages: list[list[tuple[str, str, float]]] = []   # (font, text, size)
        self._new_page()

    def _new_page(self):
        self.pages.append([])
        self._y = _PAGE_H - _MARGIN_TOP

    def line(self, text="", bold=False, size=None, gap=0.0):
        size = size or self.size
        need = self.leading + gap
        if self._y - need < _MARGIN_BOT:
            self._new_page()
        self._y -= need
        self.pages[-1].append((_FONT_B if bold else _FONT, text, size, self._y))

    def rule(self, gap=3.0):
        self.line("_" * 92, size=self.size, gap=gap)

    def save(self, path: Path):
        objs: list[bytes] = []

        def add(b: bytes) -> int:
            objs.append(b)
            return len(objs)          # 1-basierte Objektnummer

        font_r = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
                     b"/Encoding /WinAnsiEncoding >>")
        font_b = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold "
                     b"/Encoding /WinAnsiEncoding >>")
        pages_id = add(b"")           # Platzhalter, wird spaeter gefuellt
        page_ids = []
        for items in self.pages:
            buf = [b"BT"]
            for font, text, size, y in items:
                buf.append(b"/%s %.1f Tf" % (font.encode(), size))
                buf.append(b"1 0 0 1 %.2f %.2f Tm" % (_MARGIN_X, y))
                buf.append(b"(" + _enc(_esc(text)) + b") Tj")
            buf.append(b"ET")
            stream = b"\n".join(buf)
            cid = add(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
            pid = add(b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %.2f %.2f] "
                      b"/Resources << /Font << /F1 %d 0 R /F2 %d 0 R >> >> "
                      b"/Contents %d 0 R >>" % (pages_id, _PAGE_W, _PAGE_H,
                                                font_r, font_b, cid))
            page_ids.append(pid)
        objs[pages_id - 1] = (b"<< /Type /Pages /Count %d /Kids [" % len(page_ids)
                              + b" ".join(b"%d 0 R" % p for p in page_ids) + b"] >>")
        cat = add(b"<< /Type /Catalog /Pages %d 0 R >>" % pages_id)
        info = add(b"<< /Producer (x-media Business-Hub) /Creator (bh_html2pdf) >>")

        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for i, body in enumerate(objs, start=1):
            offsets.append(len(out))
            out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
        xref = len(out)
        out += b"xref\n0 %d\n" % (len(objs) + 1)
        out += b"0000000000 65535 f \n"
        for off in offsets[1:]:
            out += b"%010d 00000 n \n" % off
        out += (b"trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n"
                % (len(objs) + 1, cat, info, xref))
        Path(path).write_bytes(bytes(out))
        return bytes(out)


# ------------------------------------------------------------- Mail -> Text --

_BLOCK = r"(?:p|div|tr|br|li|h[1-6]|table|section|header|footer)"


def html_to_text(html: str) -> str:
    s = re.sub(r"(?is)<(script|style|head)[^>]*>.*?</\1>", " ", html)
    s = re.sub(r"(?i)<(?:br|/tr|/p|/div|/li|/h[1-6])\s*/?>", "\n", s)
    s = re.sub(r"(?i)</t[dh]>", "  ", s)
    s = re.sub(r"(?s)<[^>]+>", "", s)
    s = _html.unescape(s)
    s = s.replace(" ", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def mail_body_text(msg) -> str:
    """Bevorzugt text/plain, sonst HTML-Teil entschlackt."""
    plain, rich = [], []
    for part in msg.walk():
        if part.get_content_maintype() != "text":
            continue
        if part.get_filename():
            continue
        try:
            raw = part.get_payload(decode=True) or b""
            txt = raw.decode(part.get_content_charset() or "utf-8", "replace")
        except Exception:
            continue
        (plain if part.get_content_subtype() == "plain" else rich).append(txt)
    best = "\n".join(t for t in plain if t.strip())
    if len(best.strip()) < 80 and rich:
        best = html_to_text("\n".join(rich))
    elif "<" in best and ">" in best and re.search(r"(?i)<%s\b" % _BLOCK, best):
        best = html_to_text(best)          # Plaintext-Teil enthielt doch HTML
    return best.strip()


# ------------------------------------------------------------ Beleg-Erkennung --

_AMT = r"\d{1,3}(?:\.\d{3})*,\d{2}"


def _val(s: str) -> float:
    return float(s.replace(".", "").replace(",", "."))


def _amount_near(text: str, labels: list[str]):
    """Betrag aus einer beschrifteten Zeile ziehen (auch Folgezeile, HTML-Tabellen)."""
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        low = ln.lower()
        for lab in labels:
            if re.search(lab, low):
                for cand in lines[i:i + 3]:
                    ams = re.findall(_AMT, cand)
                    if ams:
                        return _val(ams[-1])
    return None


def _zahlweg_aus_text(text: str) -> tuple[str, str]:
    """-> (zielbox, zahlweg-klartext). PayPal zaehlt zur Bank (Hub-Regel)."""
    low = text.lower()
    if re.search(r"paypal", low):
        return "bank", "PayPal"
    if re.search(r"master\s*card|mastercard", low):
        return "kreditkarte_master", "Mastercard"
    if re.search(r"\bvisa\b|american express|amex", low):
        return "kreditkarte_master", "Kreditkarte"
    if re.search(r"lastschrift|sepa|abgebucht|einzug", low):
        return "bank", "Lastschrift"
    if re.search(r"\bec-?karte\b|girocard", low):
        return "bank", "EC"
    return "rechnungseingang", "offen"


def _apple(frm, subj, text):
    if not re.search(r"@(email\.)?apple\.com", frm, re.I):
        return None
    if not re.search(r"rechnung|beleg|receipt|invoice|quittung", subj, re.I):
        return None
    betrag = (_amount_near(text, [r"^\s*gesamt", r"gesamtbetrag", r"order total", r"\btotal\b"])
              or _amount_near(text, [r"mastercard", r"visa", r"paypal", r"apple pay"]))
    if betrag is None:
        ams = re.findall(_AMT, text)
        betrag = max((_val(a) for a in ams), default=None)
    nr = None
    m = re.search(r"(?:Dokument|Document)[:\s]*([0-9]{6,})", text)
    if m:
        nr = m.group(1)
    else:
        m = re.search(r"(?:Bestellnummer|Order ID)[:\s]*([A-Z0-9]{6,})", text, re.I)
        nr = m.group(1) if m else None
    box, zw = _zahlweg_aus_text(text)
    if box == "rechnungseingang":
        box, zw = "kreditkarte_master", "Kreditkarte"      # Apple bucht immer sofort ab
    return dict(quelle="Apple", absender="Apple Distribution International Ltd.",
                betrag=betrag, nummer=nr, zielbox=box, zahlweg=zw,
                datum=_datum(text), typ="eingangsrechnung")


def _paypal(frm, subj, text):
    if not re.search(r"@(\w+\.)*paypal\.(de|com)$", frm.strip("<> "), re.I):
        return None
    if not re.search(r"beleg|zahlung|payment|quittung|receipt", subj, re.I):
        return None
    betrag = (_amount_near(text, [r"gesamtbetrag dieser transaktion", r"^\s*summe\b",
                                  r"gesamtbetrag", r"\btotal\b"]))
    if betrag is None:
        ams = re.findall(_AMT, text)
        betrag = max((_val(a) for a in ams), default=None)
    m = re.search(r"Transaktionscode[:\s]*([A-Z0-9]{10,})", text, re.I)
    nr = m.group(1) if m else None
    m = re.search(r"Zahlung an\s+(.+)", text)
    empf = re.sub(r"\s+", " ", m.group(1)).strip()[:60] if m else None
    return dict(quelle="PayPal", absender=(f"PayPal-Zahlung an {empf}" if empf else "PayPal-Zahlung"),
                betrag=betrag, nummer=nr, zielbox="bank", zahlweg="PayPal",
                datum=_datum(text), typ="eingangsrechnung")


_MONATE = {"januar": 1, "februar": 2, "maerz": 3, "märz": 3, "april": 4, "mai": 5, "juni": 6,
           "juli": 7, "august": 8, "september": 9, "oktober": 10, "november": 11, "dezember": 12}


def _datum(text: str):
    m = re.search(r"(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})", text)
    if m:
        return f"{int(m.group(3)):04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.search(r"(\d{1,2})\.?\s*([A-Za-zäöü]+)\s+(\d{4})", text)
    if m and m.group(2).lower() in _MONATE:
        return f"{int(m.group(3)):04d}-{_MONATE[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"
    return None


def _csv_regeln():
    if not REGEL_CSV.exists():
        return []
    out = []
    with open(REGEL_CSV, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            muster = (r.get("Absender_Muster") or "").strip()
            if muster and not muster.startswith("#"):
                out.append(r)
    return out


def _aus_csv(frm, subj, text):
    for r in _csv_regeln():
        try:
            if not re.search(r["Absender_Muster"].strip(), frm, re.I):
                continue
            bm = (r.get("Betreff_Muster") or "").strip()
            if bm and not re.search(bm, subj, re.I):
                continue
        except re.error:
            continue
        betrag = _amount_near(text, [r"gesamtbetrag", r"rechnungsbetrag", r"zahlbetrag",
                                     r"^\s*summe\b", r"\btotal\b", r"gesamt"])
        if betrag is None:
            ams = re.findall(_AMT, text)
            betrag = max((_val(a) for a in ams), default=None)
        m = re.search(r"(?:Rechnungs-?\s*(?:nr|nummer)|Beleg-?nr|Invoice\s*(?:no|number))"
                      r"[.:\s]*([A-Z0-9][A-Z0-9/\-]{3,})", text, re.I)
        box = (r.get("Zielbox") or "").strip().lower() or _zahlweg_aus_text(text)[0]
        return dict(quelle=(r.get("Notiz") or r["Absender_Muster"]).strip(),
                    absender=frm[:80], betrag=betrag, nummer=(m.group(1) if m else None),
                    zielbox=box, zahlweg=_zahlweg_aus_text(text)[1], datum=_datum(text),
                    typ=(r.get("Typ") or "eingangsrechnung").strip())
    return None


# _paypal DEAKTIVIERT 21.08.2026 (Dirk): PayPal-Belegmails sind KEINE Rechnungen
# ("Dies ist keine Rechnung" steht drauf) — nur Zahlungsbestaetigungen. Die echte
# Rechnung muss beim Haendler (z. B. Meta/Facebook) heruntergeladen werden.
# NICHT reaktivieren. Die Zahlweg-Regel "PayPal -> Bank" (_zahlweg_aus_text) bleibt
# gueltig und ist davon unberuehrt.
REGELN = [_apple, _aus_csv]


def erkenne_beleg(frm_email: str, subject: str, body_text: str):
    """-> dict mit Belegdaten oder None. Konservativ: ohne Betrag kein Beleg."""
    if not body_text:
        return None
    for regel in REGELN:
        try:
            tr = regel(frm_email, subject or "", body_text)
        except Exception:
            tr = None
        if tr and tr.get("betrag"):
            tr["betrag"] = round(float(tr["betrag"]), 2)
            return tr
    return None


# --------------------------------------------------------------- PDF bauen --

def beleg_pdf(out_path: Path, *, treffer: dict, absender: str, betreff: str,
              mail_datum: str, empfaenger: str, body_text: str) -> bytes:
    """Erzeugt das Beleg-PDF und gibt die Bytes zurueck."""
    p = _Pdf()
    p.line("BELEG AUS E-MAIL", bold=True, size=14, gap=6)
    p.line(f"{treffer.get('quelle','')} — erzeugt vom x-media Business-Hub", size=9, gap=2)
    p.rule()
    kv = [
        ("Rechnungssteller", treffer.get("absender") or absender),
        ("Beleg-/Belegnummer", treffer.get("nummer") or "—"),
        ("Belegdatum", treffer.get("datum") or mail_datum),
        ("Betrag brutto", f"{treffer['betrag']:,.2f} EUR".replace(",", "X").replace(".", ",").replace("X", ".")),
        ("Zahlweg", treffer.get("zahlweg") or "—"),
        ("Zielbox", treffer.get("zielbox") or "—"),
        ("Empfaenger-Postfach", empfaenger),
    ]
    for k, v in kv:
        p.line(f"{k+':':24}{v}", bold=(k == "Betrag brutto"))
    p.rule(gap=6)
    p.line("Original-E-Mail", bold=True, gap=4)
    p.line(f"{'Von:':24}{absender}")
    p.line(f"{'Betreff:':24}{betreff}")
    p.line(f"{'Datum:':24}{mail_datum}")
    p.rule(gap=6)
    p.line("Inhalt der E-Mail (unveraendert)", bold=True, gap=4)
    for ln in _wrap(body_text, 96)[:400]:
        p.line(ln, size=8.5)
    p.rule(gap=6)
    p.line("Hinweis: Dieser Beleg wurde automatisch aus einer E-Mail ohne PDF-Anhang erzeugt.", size=8)
    p.line(f"Erzeugt am {datetime.now():%d.%m.%Y %H:%M} — Originalmail im Postfach {empfaenger}.", size=8)
    return p.save(out_path)


def beleg_hash(frm_email: str, betreff: str, body_text: str) -> str:
    """Stabiler Dedup-Hash (unabhaengig vom Erzeugungszeitpunkt des PDFs)."""
    norm = re.sub(r"\s+", " ", body_text).strip().lower()
    return hashlib.sha256(f"{frm_email}|{betreff}|{norm}".encode("utf-8", "replace")).hexdigest()


def dateiname(treffer: dict, mail_datum: str) -> str:
    q = re.sub(r"[^A-Za-z0-9]+", "_", (treffer.get("quelle") or "Beleg")).strip("_")[:28]
    d = (treffer.get("datum") or mail_datum or "")[:10] or datetime.now().strftime("%Y-%m-%d")
    b = f"{treffer['betrag']:.2f}".replace(".", ",")
    return f"{q}_{d}_{b}EUR.pdf"


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        t = dict(quelle="Demo", absender="Muster GmbH", betrag=29.99, nummer="123456",
                 zielbox="kreditkarte_master", zahlweg="Mastercard", datum="2026-08-20",
                 typ="eingangsrechnung")
        out = Path("/tmp/demo_beleg.pdf")
        beleg_pdf(out, treffer=t, absender="Muster <a@b.de>", betreff="Ihre Rechnung",
                  mail_datum="2026-08-20", empfaenger="info@xmedia24.com",
                  body_text="Zeile 1\nZeile 2 mit Umlauten: äöüß und 29,99 €")
        print("geschrieben:", out)
