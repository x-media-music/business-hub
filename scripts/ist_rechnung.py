#!/usr/bin/env python3
"""
ist_rechnung.py — Rechnungs-Detektor für gemischte Postfächer (v. a. info@).

Bewertet, ob ein PDF (mit optionalem Absender/Betreff) eine Rechnung ist —
über Inhalts-Merkmale, bekannte Absender (datev_routing.csv) und eine
Ignorier-Liste (ignorieren.csv). Nur Standardbibliothek + pdftotext.

Verdikt:
  RECHNUNG   → mehrere Rechnungs-Merkmale ODER bekannter Absender
  GRENZFALL  → schwache/uneindeutige Hinweise → Dirk bestätigen lassen
  KEINE      → keine Merkmale ODER auf Ignorier-Liste

Aufruf:
  python3 scripts/ist_rechnung.py datei.pdf --sender "x@y.de" --subject "..."
  python3 scripts/ist_rechnung.py module/buchhaltung/eingang/*.pdf
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
ROUTING = HUB / "module" / "buchhaltung" / "datev_routing.csv"
IGNORE = HUB / "module" / "buchhaltung" / "ignorieren.csv"

# Starke Merkmale (je 2 Punkte) — für Rechnungen sehr typisch
STRONG = {
    "Rechnungsnummer": r"rechnungs\-?\s*(nr|nummer)|invoice\s*(no|number)",
    "USt/MwSt": r"\b(ust|mwst|umsatzsteuer|vat)\b",
    "Netto/Brutto": r"\b(netto|brutto)\b",
    "Gesamtbetrag": r"gesamt(betrag|summe)|rechnungsbetrag|amount\s*due|zu\s*zahlen",
    "USt-IdNr/Steuernr": r"ust\-?id|steuernummer|steuer\-?nr|vat\s*id",
}
# Schwache Merkmale (je 1 Punkt)
WEAK = {
    "IBAN": r"\biban\b",
    "Betrag/EUR": r"\b(eur|€)\b",
    "Zahlungsziel": r"zahlungsziel|zahlbar|fällig|payment\s*terms|zahlung\s*bis",
    "Rechnung-Wort": r"\brechnung\b|\binvoice\b|\bfaktura\b",
}

SUBJECT_HINT = r"rechnung|invoice|faktura|beleg|receipt|zahlung|rechnungsnr"


def pdf_text(path: Path) -> str:
    try:
        out = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                             capture_output=True, timeout=30)
        if out.returncode == 0:
            return out.stdout.decode("utf-8", "ignore")
    except Exception:  # noqa: BLE001
        pass
    try:
        import pdfplumber  # type: ignore
        with pdfplumber.open(str(path)) as pdf:
            return "\n".join((p.extract_text() or "") for p in pdf.pages)
    except Exception:  # noqa: BLE001
        return ""


def load_col(path: Path, col: int = 0) -> list[str]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh, delimiter=";"))
    return [r[col].strip().lower() for r in rows[1:] if r and r[col].strip()]


def sender_matches(sender: str, names: list[str]) -> str | None:
    s = sender.lower()
    for n in names:
        # Vergleich über die ersten Wort-Token des hinterlegten Namens
        token = re.split(r"[ (/]", n)[0]
        if token and (token in s or n in s):
            return n
    return None


def score_pdf(path: Path, sender: str = "", subject: str = "") -> dict:
    text = pdf_text(path).lower()
    hits_strong = [k for k, pat in STRONG.items() if re.search(pat, text)]
    hits_weak = [k for k, pat in WEAK.items() if re.search(pat, text)]
    pts = 2 * len(hits_strong) + len(hits_weak)

    known = sender_matches(sender, load_col(ROUTING)) if sender else None
    ignored = sender_matches(sender, load_col(IGNORE)) if sender else None
    subj_hit = bool(re.search(SUBJECT_HINT, subject, re.I)) if subject else False

    if ignored:
        verdict = "KEINE"
    elif known:
        verdict = "RECHNUNG"
    elif pts >= 6 or (len(hits_strong) >= 3):
        verdict = "RECHNUNG"
    elif pts >= 2 or subj_hit:
        verdict = "GRENZFALL"
    else:
        verdict = "KEINE"

    return {"datei": path.name, "verdikt": verdict, "punkte": pts,
            "stark": hits_strong, "schwach": hits_weak,
            "bekannt": known, "ignoriert": ignored, "betreff_hinweis": subj_hit}


def main() -> int:
    ap = argparse.ArgumentParser(description="Rechnungs-Detektor")
    ap.add_argument("pdfs", nargs="+")
    ap.add_argument("--sender", default="")
    ap.add_argument("--subject", default="")
    args = ap.parse_args()

    for p in args.pdfs:
        path = Path(p)
        if not path.exists():
            print(f"?? fehlt: {p}"); continue
        r = score_pdf(path, args.sender, args.subject)
        mark = {"RECHNUNG": "🧾", "GRENZFALL": "⚠️ ", "KEINE": "  "}[r["verdikt"]]
        extra = f" [bekannt: {r['bekannt']}]" if r["bekannt"] else (f" [ignoriert: {r['ignoriert']}]" if r["ignoriert"] else "")
        print(f"{mark} {r['verdikt']:9} ({r['punkte']} P.) {r['datei']}{extra}")
        if r["stark"] or r["schwach"]:
            print(f"      Merkmale: {', '.join(r['stark'] + r['schwach'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
