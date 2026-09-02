#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Darlehens-Verwaltung fuer den Business-Hub (x-media music GmbH / x-media event GmbH).

Fuehrt ein Darlehenskonto als Staffelrechnung mit taggenauen Zinsen (act/365) und
erzeugt ein finanzamtfaehiges Datenblatt + Zins-/Tilgungsverlauf als PDF.

Datenhaltung (Semikolon/UTF-8, wie im Hub ueblich):
  module/darlehen/stammdaten_<slug>.csv   Feld;Wert
  module/darlehen/darlehen_<slug>.csv     Datum;Vorgang;Betrag;Beleg;Notiz
     Vorgang: AUSZAHLUNG | TILGUNG | ZINSZAHLUNG | ERHOEHUNG

Aufrufe:
  python3 scripts/darlehen.py --status  janis_herb
  python3 scripts/darlehen.py --buchen  janis_herb --datum 30.09.2026 --vorgang TILGUNG \
                              --betrag 150 --beleg "RG 09/2026" --notiz "Verrechnung Gage"
  python3 scripts/darlehen.py --pdf     janis_herb [--stichtag 31.12.2026]

Rechenweg (dokumentiert, damit er pruefbar bleibt):
  Zins je Abschnitt = Restschuld_vorher * Zinssatz * Ist-Tage / 365, kaufmaennisch auf
  2 Nachkommastellen gerundet. Der Zins wird der Restschuld zugeschlagen, danach wird
  die Tilgung abgezogen.  Neue Restschuld = alte Restschuld + Zins - Tilgung.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODUL = os.path.join(HUB, "module", "darlehen")
REPORTS = os.path.join(HUB, "reports")
ANSICHT = os.path.join(HUB, "Ansicht Dokumente", "hub_Owner")


# ---------------------------------------------------------------- Hilfsmittel
def r2(x) -> Decimal:
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def eur(x) -> str:
    s = f"{r2(x):,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def d(s: str) -> date:
    return datetime.strptime(s.strip(), "%d.%m.%Y").date()


def dez(s: str) -> Decimal:
    return Decimal(str(s).strip().replace(".", "").replace(",", "."))


def lies_stammdaten(slug: str) -> dict:
    p = os.path.join(MODUL, f"stammdaten_{slug}.csv")
    with open(p, encoding="utf-8") as f:
        return {r[0].strip(): r[1].strip() for r in csv.reader(f, delimiter=";")
                if len(r) >= 2 and r[0].strip() and r[0].strip() != "Feld"}


def lies_bewegungen(slug: str) -> list[dict]:
    p = os.path.join(MODUL, f"darlehen_{slug}.csv")
    with open(p, encoding="utf-8") as f:
        rows = [r for r in csv.reader(f, delimiter=";") if r and r[0].strip()]
    out = []
    for r in rows[1:]:
        r = r + [""] * (5 - len(r))
        out.append({"datum": d(r[0]), "vorgang": r[1].strip().upper(),
                    "betrag": dez(r[2]), "beleg": r[3].strip(), "notiz": r[4].strip()})
    out.sort(key=lambda x: x["datum"])
    return out


# ---------------------------------------------------------------- Rechenkern
def verlauf(slug: str, stichtag: date | None = None) -> tuple[list[dict], dict]:
    """Baut den Staffelverlauf. Gibt (Zeilen, Summen) zurueck."""
    stamm = lies_stammdaten(slug)
    zins = dez(stamm["Zinssatz_p_a"]) / Decimal(100)
    bew = lies_bewegungen(slug)
    if stichtag:
        bew = [b for b in bew if b["datum"] <= stichtag]

    zeilen, saldo, vor = [], Decimal(0), None
    z_sum = t_sum = a_sum = Decimal(0)

    for b in bew:
        if vor is None:
            saldo = b["betrag"]
            a_sum += b["betrag"]
            zeilen.append({**b, "tage": None, "zins": None, "saldo": saldo})
        else:
            tage = (b["datum"] - vor).days
            z = r2(saldo * zins * Decimal(tage) / Decimal(365))
            saldo = saldo + z
            if b["vorgang"] in ("TILGUNG", "ZINSZAHLUNG"):
                saldo -= b["betrag"]
                t_sum += b["betrag"]
            else:  # ERHOEHUNG / weitere AUSZAHLUNG
                saldo += b["betrag"]
                a_sum += b["betrag"]
            z_sum += z
            zeilen.append({**b, "tage": tage, "zins": z, "saldo": saldo})
        vor = b["datum"]

    # Zinsabgrenzung bis zum Stichtag (falls nach der letzten Bewegung)
    abgrenzung = None
    if stichtag and vor and stichtag > vor:
        tage = (stichtag - vor).days
        z = r2(saldo * zins * Decimal(tage) / Decimal(365))
        abgrenzung = {"datum": stichtag, "tage": tage, "zins": z, "saldo": saldo + z}
        z_sum += z
        saldo += z

    return zeilen, {"auszahlung": a_sum, "tilgung": t_sum, "zinsen": r2(z_sum),
                    "saldo": r2(saldo), "abgrenzung": abgrenzung,
                    "letztes_datum": vor, "stamm": stamm}


# ---------------------------------------------------------------- Ausgaben
def status(slug: str, stichtag: date | None = None) -> None:
    zeilen, s = verlauf(slug, stichtag)
    st = s["stamm"]
    print(f"\nDarlehen {st['Darlehensnehmer']}  ({st['Darlehensgeber']})")
    print(f"Auszahlung {st['Auszahlungsdatum']} · {eur(dez(st['Darlehensbetrag']))} "
          f"· {st['Zinssatz_p_a']} % p. a. · {st['Zinsmethode']}\n")
    kopf = f"{'Datum':<12}{'Vorgang':<12}{'Tage':>5}{'Zins':>12}{'Betrag':>13}{'Restschuld':>14}   Beleg"
    print(kopf)
    print("-" * (len(kopf) + 10))
    for z in zeilen:
        print(f"{z['datum'].strftime('%d.%m.%Y'):<12}{z['vorgang'].title():<12}"
              f"{(z['tage'] if z['tage'] is not None else '-'):>5}"
              f"{(eur(z['zins']) if z['zins'] is not None else '-'):>12}"
              f"{eur(z['betrag']):>13}{eur(z['saldo']):>14}   {z['beleg']}")
    if s["abgrenzung"]:
        a = s["abgrenzung"]
        print(f"{a['datum'].strftime('%d.%m.%Y'):<12}{'Abgrenzung':<12}{a['tage']:>5}"
              f"{eur(a['zins']):>12}{'':>13}{eur(a['saldo']):>14}   (Zinsabgrenzung Stichtag)")
    print("-" * (len(kopf) + 10))
    print(f"Ausgereicht {eur(s['auszahlung'])} · getilgt {eur(s['tilgung'])} "
          f"· Zinsen {eur(s['zinsen'])} · RESTSCHULD {eur(s['saldo'])}\n")


def buchen(slug: str, datum: str, vorgang: str, betrag: str, beleg: str, notiz: str) -> None:
    p = os.path.join(MODUL, f"darlehen_{slug}.csv")
    dat = d(datum)
    vorgang = vorgang.strip().upper()
    if vorgang not in ("AUSZAHLUNG", "TILGUNG", "ZINSZAHLUNG", "ERHOEHUNG"):
        sys.exit(f"Unbekannter Vorgang: {vorgang}")
    for b in lies_bewegungen(slug):
        if b["datum"] == dat and b["vorgang"] == vorgang and b["betrag"] == dez(betrag):
            sys.exit("Diese Buchung steht bereits in der Datei (Dublettenschutz).")
    betr = f"{r2(dez(betrag)):.2f}".replace(".", ",")
    with open(p, "a", encoding="utf-8", newline="") as f:
        csv.writer(f, delimiter=";").writerow(
            [dat.strftime("%d.%m.%Y"), vorgang, betr, beleg, notiz])
    print(f"Gebucht: {dat.strftime('%d.%m.%Y')} {vorgang} {eur(dez(betrag))} ({beleg})")
    status(slug)


# ---------------------------------------------------------------- PDF
def pdf(slug: str, stichtag: date | None = None) -> str:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                    TableStyle, KeepTogether)

    zeilen, s = verlauf(slug, stichtag)
    st = s["stamm"]
    heute = date.today()
    stand = stichtag or s["letztes_datum"]

    os.makedirs(REPORTS, exist_ok=True)
    name = f"Darlehen_{st['Darlehensnehmer'].replace(' ', '_')}_Datenblatt_{stand:%Y-%m-%d}.pdf"
    ziel = os.path.join(REPORTS, name)

    ss = getSampleStyleSheet()
    H = ParagraphStyle("H", parent=ss["Heading1"], fontSize=15, spaceAfter=2,
                       textColor=colors.HexColor("#111111"))
    SUB = ParagraphStyle("SUB", parent=ss["Normal"], fontSize=9,
                         textColor=colors.HexColor("#555555"), spaceAfter=10)
    H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=11, spaceBefore=12,
                        spaceAfter=5, textColor=colors.HexColor("#111111"))
    N = ParagraphStyle("N", parent=ss["Normal"], fontSize=8.5, leading=12)
    KL = ParagraphStyle("KL", parent=ss["Normal"], fontSize=7.5, leading=10,
                        textColor=colors.HexColor("#555555"))

    doc = SimpleDocTemplate(ziel, pagesize=A4, topMargin=18 * mm, bottomMargin=16 * mm,
                            leftMargin=18 * mm, rightMargin=18 * mm,
                            title=f"Darlehens-Datenblatt {st['Darlehensnehmer']}",
                            author=st["Darlehensgeber"])
    F = []
    F.append(Paragraph("Darlehens-Datenblatt und Zins-/Tilgungsverlauf", H))
    F.append(Paragraph(
        f"{st['Darlehensgeber']} &ndash; Darlehen an {st['Darlehensnehmer']} "
        f"&middot; Stand {stand:%d.%m.%Y} &middot; erstellt am {heute:%d.%m.%Y}", SUB))

    # --- Stammdaten
    def zeile(k, v):
        return [Paragraph(f"<b>{k}</b>", N), Paragraph(str(v), N)]

    stamm_rows = [
        zeile("Darlehensgeber", f"{st['Darlehensgeber']}, {st['Darlehensgeber_Adresse']}<br/>"
                               f"vertreten durch {st['Darlehensgeber_Vertreter']}"),
        zeile("Darlehensnehmer", f"{st['Darlehensnehmer']}<br/>{st['Darlehensnehmer_Kontakt']}"),
        zeile("Darlehensbetrag", eur(dez(st["Darlehensbetrag"]))),
        zeile("Auszahlung am", st["Auszahlungsdatum"]),
        zeile("Zinssatz", f"{st['Zinssatz_p_a']} % p. a."),
        zeile("Zinsmethode", st["Zinsmethode"]),
        zeile("Zinsverrechnung", st["Zinsverrechnung"]),
        zeile("Tilgungsform", st["Tilgungsform"]),
        zeile("Endf&auml;lligkeit", st.get("Endfaelligkeit", "—")),
        zeile("Sicherheiten", st.get("Sicherheiten", "—")),
        zeile("Darlehensvertrag", f"{st.get('Vertrag_Datum', '—')} &middot; "
                                  f"{st.get('Vertrag_Ablage', '—')}"),
    ]
    t = Table(stamm_rows, colWidths=[42 * mm, 132 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, colors.HexColor("#DDDDDD")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BBBBBB")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F7F7F7")),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    F.append(Paragraph("1. Stammdaten", H2))
    F.append(t)

    # --- Verlauf
    F.append(Paragraph("2. Zins- und Tilgungsverlauf (Staffelrechnung)", H2))
    kopf = ["Datum", "Vorgang", "Tage", "Zins", "Auszahlung /<br/>Tilgung", "Restschuld",
            "Beleg / Bemerkung"]
    data = [[Paragraph(f"<b>{k}</b>", N) for k in kopf]]
    for z in zeilen:
        bem = z["beleg"]
        if z["notiz"]:
            bem = f"{bem}<br/>{z['notiz']}" if bem else z["notiz"]
        data.append([
            Paragraph(z["datum"].strftime("%d.%m.%Y"), N),
            Paragraph(z["vorgang"].title(), N),
            Paragraph(str(z["tage"]) if z["tage"] is not None else "–", N),
            Paragraph(eur(z["zins"]) if z["zins"] is not None else "–", N),
            Paragraph(eur(z["betrag"]), N),
            Paragraph(f"<b>{eur(z['saldo'])}</b>", N),
            Paragraph(bem or "", KL),
        ])
    if s["abgrenzung"]:
        a = s["abgrenzung"]
        data.append([
            Paragraph(a["datum"].strftime("%d.%m.%Y"), N),
            Paragraph("Abgrenzung", N), Paragraph(str(a["tage"]), N),
            Paragraph(eur(a["zins"]), N), Paragraph("–", N),
            Paragraph(f"<b>{eur(a['saldo'])}</b>", N),
            Paragraph("Zinsabgrenzung bis Stichtag (noch nicht verrechnet)", KL),
        ])
    data.append([
        Paragraph("<b>Summe</b>", N), Paragraph("", N), Paragraph("", N),
        Paragraph(f"<b>{eur(s['zinsen'])}</b>", N),
        Paragraph(f"<b>getilgt {eur(s['tilgung'])}</b>", N),
        Paragraph(f"<b>{eur(s['saldo'])}</b>", N),
        Paragraph("Restschuld zum Stichtag", KL),
    ])
    tv = Table(data, colWidths=[19 * mm, 20 * mm, 10 * mm, 19 * mm, 24 * mm, 25 * mm, 57 * mm],
               repeatRows=1)
    tv.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EFEFEF")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F7F7F7")),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#999999")),
        ("LINEABOVE", (0, -1), (-1, -1), 0.6, colors.HexColor("#999999")),
        ("LINEBELOW", (0, 1), (-1, -2), 0.25, colors.HexColor("#DDDDDD")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BBBBBB")),
        ("ALIGN", (2, 1), (5, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    F.append(tv)

    # --- Zusammenfassung
    F.append(Paragraph("3. Zusammenfassung zum Stichtag", H2))
    zus = [
        [Paragraph("<b>Ausgereichtes Darlehen</b>", N), Paragraph(eur(s["auszahlung"]), N)],
        [Paragraph("<b>Bisher getilgt</b>", N), Paragraph(eur(s["tilgung"]), N)],
        [Paragraph("<b>Aufgelaufene Zinsen</b>", N), Paragraph(eur(s["zinsen"]), N)],
        [Paragraph("<b>Restschuld (Kapital + kapitalisierte Zinsen)</b>", N),
         Paragraph(f"<b>{eur(s['saldo'])}</b>", N)],
    ]
    tz = Table(zus, colWidths=[110 * mm, 30 * mm])
    tz.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, colors.HexColor("#DDDDDD")),
        ("LINEABOVE", (0, -1), (-1, -1), 0.6, colors.HexColor("#999999")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BBBBBB")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    F.append(tz)

    # --- Rechenweg / Erlaeuterung
    F.append(Paragraph("4. Rechenweg und Erl&auml;uterungen", H2))
    F.append(Paragraph(
        "<b>Zinsberechnung:</b> Die Zinsen werden taggenau nach der Staffelmethode ermittelt. "
        "F&uuml;r jeden Abschnitt zwischen zwei Bewegungen gilt: "
        "<i>Zins = Restschuld &times; Zinssatz &times; tats&auml;chliche Tage / 365</i>, "
        "kaufm&auml;nnisch auf zwei Nachkommastellen gerundet. Der Zins wird der Restschuld "
        "zugeschlagen; anschlie&szlig;end wird die Tilgung abgesetzt.", N))
    F.append(Spacer(1, 4))
    F.append(Paragraph(
        "<b>Tilgung durch Verrechnung:</b> Die Tilgungen erfolgen durch Aufrechnung mit "
        "Gagenrechnungen des Darlehensnehmers. Die jeweilige Eingangsrechnung wird in voller "
        "H&ouml;he als Aufwand erfasst; ausgezahlt wird nur der um den Tilgungsbetrag "
        "gek&uuml;rzte Betrag. Die Differenz mindert die Darlehensforderung. Der Tilgungsbetrag "
        "ist auf der jeweiligen Rechnung bzw. im Zahlungsbeleg vermerkt.", N))
    F.append(Spacer(1, 4))
    F.append(Paragraph(
        "<b>Nachweise:</b> Auszahlungsbeleg, Darlehensvertrag und die in Spalte "
        "&bdquo;Beleg&ldquo; genannten Eingangsrechnungen sind Bestandteil der Buchf&uuml;hrung "
        "und dort abgelegt.", N))
    F.append(Spacer(1, 10))
    F.append(Paragraph(
        "Erstellt aus dem gef&uuml;hrten Darlehenskonto des Business-Hubs "
        f"(module/darlehen/darlehen_{slug}.csv). Dieses Datenblatt ersetzt keine "
        "steuerliche Beratung.", KL))
    F.append(Spacer(1, 14))

    unter = Table([[Paragraph("_______________________________<br/>Ort, Datum", KL),
                    Paragraph("_______________________________<br/>"
                              f"{st['Darlehensgeber_Vertreter']}", KL)]],
                  colWidths=[87 * mm, 87 * mm])
    unter.setStyle(TableStyle([("TOPPADDING", (0, 0), (-1, -1), 10),
                               ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    F.append(KeepTogether(unter))

    doc.build(F)

    if os.path.isdir(ANSICHT):
        import shutil
        shutil.copy2(ziel, os.path.join(ANSICHT, name))
    return ziel


# ---------------------------------------------------------------- CLI
def main() -> None:
    ap = argparse.ArgumentParser(description="Darlehenskonto fuehren + Datenblatt erzeugen")
    ap.add_argument("slug", help="z. B. janis_herb")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--buchen", action="store_true")
    ap.add_argument("--datum"); ap.add_argument("--vorgang"); ap.add_argument("--betrag")
    ap.add_argument("--beleg", default=""); ap.add_argument("--notiz", default="")
    ap.add_argument("--stichtag", help="TT.MM.JJJJ - Zinsabgrenzung bis zu diesem Tag")
    a = ap.parse_args()

    stichtag = d(a.stichtag) if a.stichtag else None
    if a.buchen:
        if not (a.datum and a.vorgang and a.betrag):
            sys.exit("--buchen braucht --datum --vorgang --betrag")
        buchen(a.slug, a.datum, a.vorgang, a.betrag, a.beleg, a.notiz)
    elif a.pdf:
        p = pdf(a.slug, stichtag)
        print("PDF erstellt:", p)
    else:
        status(a.slug, stichtag)


if __name__ == "__main__":
    main()
