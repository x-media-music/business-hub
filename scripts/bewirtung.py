#!/usr/bin/env python3
"""
bewirtung.py — erzeugt ein Bewirtungsbeleg-Zusatzblatt (PDF) und führt es mit
dem eingescannten Beleg zu EINEM PDF zusammen.

Zusatzblatt-Felder (§ 4 Abs. 5 Satz 1 Nr. 2 EStG):
  Tag, Ort/Gaststätte, Anlass, bewirtete Personen, Bewirtender, Betrag, Zahlweg,
  Unterschriftsfeld.

Erzeugen benötigt reportlab (pip install reportlab --break-system-packages),
Zusammenführen nutzt pdfunite (poppler).

Beispiel:
  python3 scripts/bewirtung.py \
    --scan beleg.pdf --datum 2026-07-01 --ort "Ristorante Roma, Stuttgart" \
    --betrag "84,50 €" --zahlweg bar --firma music \
    --teilnehmer "Max Mustermann (Fa. Y); Anna Beispiel (Fa. Z)" \
    --anlass "Besprechung Booking Sommerfest 2026"

Ausgabe: module/buchhaltung/bewirtung/Bewirtung_JJJJ-MM-TT_<Ort>.pdf
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
OUTDIR = HUB / "module" / "buchhaltung" / "bewirtung"

FIRMEN = {
    "music": "x-media music GmbH",
    "event": "x-media event GmbH",
}
ZAHLWEG = {"bar": "bar (Kasse)", "ec": "EC-/Girocard (Bank)"}


def slug(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", s, flags=re.U).strip().replace(" ", "-")
    return re.sub(r"-+", "-", s)[:40] or "Ort"


def make_zusatzblatt(pdf_path: Path, a) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    W, H = A4
    x = 25 * mm
    y = H - 25 * mm

    c.setFont("Helvetica-Bold", 15)
    c.drawString(x, y, "Bewirtungsbeleg – Eigenbeleg")
    y -= 6 * mm
    c.setFont("Helvetica", 9)
    c.drawString(x, y, "Angaben gemäß § 4 Abs. 5 Satz 1 Nr. 2 EStG (Zusatzblatt zur beigefügten Rechnung)")
    y -= 5 * mm
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(x, y, FIRMEN.get(a.firma, a.firma) + " · Dirk Wöhrle")
    y -= 10 * mm
    c.line(x, y, W - 25 * mm, y)
    y -= 12 * mm

    def field(label: str, value: str, lines: list[str] | None = None) -> None:
        nonlocal y
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, label)
        c.setFont("Helvetica", 11)
        if lines:
            for ln in lines:
                y -= 6 * mm
                c.drawString(x + 6 * mm, y, ln)
        else:
            c.drawString(x + 55 * mm, y, value)
        y -= 11 * mm

    field("Tag der Bewirtung:", a.datum)
    field("Ort der Bewirtung:", a.ort)
    teilnehmer = [t.strip() for t in re.split(r"[;\n]", a.teilnehmer) if t.strip()]
    field("Bewirtete Personen:", "", teilnehmer)
    field("Bewirtende Person:", "Dirk Wöhrle (" + FIRMEN.get(a.firma, a.firma) + ")")
    field("Anlass der Bewirtung:", "", [a.anlass])
    field("Höhe der Aufwendungen:", a.betrag)
    field("Zahlweg:", ZAHLWEG.get(a.zahlweg.lower(), a.zahlweg))

    y -= 8 * mm
    c.line(x, y, W - 25 * mm, y)
    y -= 16 * mm
    c.setFont("Helvetica", 10)
    c.drawString(x, y, "Ort, Datum")
    c.drawString(x + 95 * mm, y, "Unterschrift Bewirtender")
    c.line(x, y + 10 * mm, x + 70 * mm, y + 10 * mm)
    c.line(x + 95 * mm, y + 10 * mm, W - 25 * mm, y + 10 * mm)

    c.setFont("Helvetica-Oblique", 8)
    c.drawString(x, 18 * mm, "Automatisch erzeugt vom x-media Business-Hub. Beleg (Rechnung) ist auf den Folgeseiten beigefügt.")
    c.showPage()
    c.save()


def image_to_pdf(img: Path, out: Path) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(str(out), pagesize=A4)
    W, H = A4
    ir = ImageReader(str(img))
    iw, ih = ir.getSize()
    scale = min((W - 40) / iw, (H - 40) / ih)
    c.drawImage(ir, (W - iw * scale) / 2, (H - ih * scale) / 2,
                iw * scale, ih * scale, preserveAspectRatio=True)
    c.showPage()
    c.save()


def main() -> int:
    ap = argparse.ArgumentParser(description="Bewirtungsbeleg-Zusatzblatt + Merge")
    ap.add_argument("--scan", required=True, help="eingescannter Beleg (PDF oder Bild)")
    ap.add_argument("--datum", required=True)
    ap.add_argument("--ort", required=True)
    ap.add_argument("--betrag", required=True)
    ap.add_argument("--zahlweg", required=True, choices=["bar", "ec", "EC", "Bar"])
    ap.add_argument("--firma", required=True, choices=["music", "event"])
    ap.add_argument("--teilnehmer", required=True)
    ap.add_argument("--anlass", required=True)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    scan = Path(args.scan)
    if not scan.exists():
        sys.exit(f"❌ Scan nicht gefunden: {scan}")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    out = Path(args.out) if args.out else OUTDIR / f"Bewirtung_{args.datum}_{slug(args.ort)}.pdf"

    with tempfile.TemporaryDirectory() as td:
        zus = Path(td) / "zusatzblatt.pdf"
        make_zusatzblatt(zus, args)

        # Scan ggf. von Bild zu PDF wandeln
        if scan.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            scan_pdf = Path(td) / "scan.pdf"
            image_to_pdf(scan, scan_pdf)
        elif scan.suffix.lower() == ".pdf":
            # Verschlüsselung/Eigenheiten entfernen (qpdf), damit pdfunite mergen kann
            scan_pdf = Path(td) / "scan.pdf"
            q = subprocess.run(["qpdf", "--decrypt", "--", str(scan), str(scan_pdf)],
                             capture_output=True)
            if q.returncode not in (0, 3) or not scan_pdf.exists():  # 3 = warnings
                scan_pdf = scan  # Fallback: Original versuchen
        else:
            sys.exit(f"❌ Nicht unterstütztes Scan-Format: {scan.suffix} (PDF/JPG/PNG)")

        r = subprocess.run(["pdfunite", str(zus), str(scan_pdf), str(out)],
                          capture_output=True)
        if r.returncode != 0:
            sys.exit(f"❌ pdfunite-Fehler: {r.stderr.decode('utf-8','ignore')}")

    box = "Kasse" if args.zahlweg.lower() == "bar" else "Bank"
    ziel = "DATEV-Uploadmail" if args.firma == "music" else "Dropbox (event)"
    print(f"✅ Bewirtungsbeleg erstellt: {out}")
    print(f"   Firma: {FIRMEN[args.firma]} · Zahlweg: {args.zahlweg} → Box {box} ({ziel})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
