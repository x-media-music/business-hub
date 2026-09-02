#!/usr/bin/env python3
"""
bh_ingest.py — Hub-Ingest fuer die Buchhaltung (Hub fuehrt, App = Anzeige+Freigabe).

Zieht die 4 Postfaecher inkrementell, erkennt Rechnungen (ist_rechnung.py),
routet ueber datev_routing.csv, merged bekannte Mehrfach-PDF-Absender (UTA),
erzeugt fuer Belegmails OHNE PDF-Anhang selbst ein PDF (bh_html2pdf.py: Apple,
PayPal & Co. — erweiterbar ueber module/buchhaltung/html_belege.csv),
laedt das PDF in den Supabase-Storage-Bucket 'belege' und legt den Beleg in
bh_belege mit status='warte_bestaetigung' an (erscheint in der App unter
"Wartend"). Dirk gibt in der App frei -> bh_send.py liefert aus.

Sicher by design:
  - rechnung@ (dediziertes Belegpostfach) offensiv: alles ausser KEINE.
  - info@ (gemischt) konservativ: nur RECHNUNG (bekannter Absender / klare Merkmale).
  - Dedup ueber pdf_hash gegen den Bestand.
  - Nichts wird versendet/verschoben — nur vorbereitet (frei ohne Gate).
  - UTA: stehende Freigabe -> direkt dirk_entscheidung='freigegeben' (autonom).

Aufruf:
  python3 scripts/bh_ingest.py --dry-run     # nur anzeigen, was angelegt wuerde
  python3 scripts/bh_ingest.py               # anlegen
  python3 scripts/bh_ingest.py --box rechnung   # nur ein Postfach
  python3 scripts/bh_ingest.py --box info --from-uid 139340 --dry-run   # Nachlauf ab UID
  python3 scripts/bh_ingest.py --box info --only-uid 139156             # genau eine Mail nachziehen
"""
from __future__ import annotations
import os, sys, re, json, ssl, imaplib, email, hashlib, subprocess, urllib.request, urllib.parse, csv
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bh_html2pdf as h2p   # Belege aus Mails OHNE PDF-Anhang (Apple, PayPal ...)

HUB = Path(__file__).resolve().parent.parent
S = HUB / "scripts"
MAIL_ENV = S / "mail.env"
KEYS = S / "buchhaltung_keys.env"
ROUTING = HUB / "module" / "buchhaltung" / "datev_routing.csv"
IGNOR = HUB / "module" / "buchhaltung" / "ignorieren.csv"
CURSOR = HUB / "module" / "buchhaltung" / "ingest_cursor.json"
WORK = HUB / "module" / "buchhaltung" / "review" / "ingest"
WORK.mkdir(parents=True, exist_ok=True)

BOXES = {  # box -> (env-prefix, firma, offensiv?)
    "rechnung":       ("MAIL_RECHNUNG",       "music", True),
    "info":           ("MAIL_INFO",           "music", False),
    "rechnung_event": ("MAIL_RECHNUNG_EVENT", "event", True),
    "info_event":     ("MAIL_INFO_EVENT",     "event", False),
}
DATEV_BOXES = {
    "bank":"06aa928a-7817-4bcf-a4ef-c2185efe6c35@uploadmail.datev.de",
    "rechnungseingang":"5cc1bdc1-f56a-4718-b6da-325b7939246d@uploadmail.datev.de",
    "kreditkarte_master":"abd46470-258e-4ebd-92d2-4c18b26fe595@uploadmail.datev.de",
    "kasse":"868708a5-cb99-4ab3-ae70-0c71199e0f8a@uploadmail.datev.de",
    "rechnungsausgang":"9616a328-2fcb-4f57-8df0-768c803106c7@uploadmail.datev.de",
}
MERGE_SENDER = {"uta": ["RE", "GSB", "EPN"]}   # Absender-Keyword -> Reihenfolge der PDF-Typen

def load_env(p):
    e={}
    for ln in p.read_text(encoding="utf-8").splitlines():
        ln=ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k,v=ln.split("=",1); e[k.strip()]=v.strip()
    return e

MENV=load_env(MAIL_ENV); KENV=load_env(KEYS)
SB_URL=KENV["SUPABASE_URL"].rstrip("/"); SB_KEY=KENV["SUPABASE_SERVICE_ROLE_KEY"]
IMAP_HOST=MENV["IMAP_HOST"]; IMAP_PORT=int(MENV.get("IMAP_PORT",993))

def sb(method,path,data=None,raw=None,ctype="application/json"):
    h={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":ctype}
    body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
    r=urllib.request.Request(SB_URL+path,data=body,method=method,headers=h)
    try:
        with urllib.request.urlopen(r) as x:
            b=x.read(); return x.status,(json.loads(b) if b and ctype=="application/json" else b)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")

def load_routing():
    rows=[]
    with open(ROUTING,encoding="utf-8") as f:
        for r in csv.DictReader(f,delimiter=";"):
            rows.append(r)
    return rows
ROUTES=load_routing()
IGNORE=set()
if IGNOR.exists():
    for r in csv.DictReader(open(IGNOR,encoding="utf-8"),delimiter=";"):
        IGNORE.add((r.get("Absender") or "").lower())

def cursors():
    return json.loads(CURSOR.read_text()) if CURSOR.exists() else {}
def save_cursors(c):
    CURSOR.write_text(json.dumps(c,indent=2))

def dh(s): return str(make_header(decode_header(s or "")))

GENERIC={"gmbh","co","kg","und","ohg","mbh","the","ltd","inc","pbc","gbr","alias",
         # generische Branchen-/Ortswoerter -> zu unspezifisch zum Matchen:
         "events","event","media","music","stuttgart","records","pictures","lighting",
         "technik","veranstaltungstechnik","service","sicherheit","fahrzeugbau","reifen",
         "management","backline","catering","hotel","restaurant"}
def _ist_personenname(rn):
    """'Jonas Schoof' = Personenname, 'Mediapool Veranstaltungstechnik GmbH' nicht."""
    w=re.findall(r"[a-zäöüß]+", rn)
    return len(w)==2 and all(len(x)>=3 for x in w) and not (set(w) & GENERIC)

def match_route(absender_name, absender_email):
    """Streng: matcht nur, wenn ein distinktives Token (>=4 Zeichen, nicht generisch)
    des Rechnungsstellers im Absender vorkommt. Verhindert Fehltreffer wie 'ts'->'events'.
    Bei Personennamen (Vorname Nachname) muessen BEIDE Teile vorkommen — sonst matcht
    ein blosser Vorname den falschen Menschen (Fall 31.08.2026: Jonas Hafner wurde als
    Jonas Schoof gefuehrt, samt dessen Zahlungsdaten)."""
    hay=f"{absender_name} {absender_email}".lower()
    for r in ROUTES:
        rn=(r.get("Rechnungssteller") or "").split("(")[0].lower()
        toks=[w for w in re.findall(r"[a-zäöüß0-9]{4,}",rn) if w not in GENERIC]
        if not toks: continue
        if _ist_personenname(rn):
            if all(t in hay for t in toks): return r
        elif any(t in hay for t in toks):
            return r
    return None

def rgnr_exists(rgnr, firma):
    if not rgnr: return False
    st,d=sb("GET","/rest/v1/bh_belege?select=id&rechnungsnummer=eq."+urllib.parse.quote(rgnr)+f"&firma=eq.{firma}")
    return isinstance(d,list) and len(d)>0

def box_from_route(route, firma):
    z=(route.get("Zielbox") or "").lower() if route else ""
    zw=(route.get("Zahlweg") or "").lower() if route else ""
    zahlungsstatus = ("bezahlt_lastschrift" if "lastschrift" in zw else
                      "bezahlt_kreditkarte" if ("kreditkarte" in zw or "master" in zw) else
                      "bezahlt_ec" if " ec" in zw else "offen")
    if firma=="music":
        if "bank" in z: kat="bank"
        elif "kreditkarte" in z or "master" in z: kat="kreditkarte_master"
        elif "kasse" in z: kat="kasse"
        elif "rechnungsausgang" in z: kat="rechnungsausgang"
        else: kat="rechnungseingang"
        return dict(datev_kategorie=kat, datev_email=DATEV_BOXES[kat], dropbox_ordner=None, zahlungsstatus=zahlungsstatus)
    else:
        if "bezahlte" in z and "master" in z: ordner="XE bezahlte Eingangsrechnungen/Master"
        elif "bezahlte" in z: ordner="XE bezahlte Eingangsrechnungen"
        elif "kasse" in z: ordner="XE Kassenbelege"
        elif "ausgang" in z: ordner="XE offene Ausgangsrechnugnen"
        else: ordner="XE offene Eingangsrechnungen"
        return dict(datev_kategorie=None, datev_email=None, dropbox_ordner=ordner, zahlungsstatus=zahlungsstatus)

def box_from_kategorie(kat, firma, zahlweg=""):
    """Zielbox direkt aus einer Kategorie (fuer HTML-Belege ohne Routing-Eintrag)."""
    kat = (kat or "rechnungseingang").lower()
    zahlungsstatus = ("bezahlt_kreditkarte" if kat == "kreditkarte_master" else
                      "bezahlt_lastschrift" if kat == "bank" else
                      "bar" if kat == "kasse" else "offen")
    if firma == "music":
        if kat not in DATEV_BOXES: kat = "rechnungseingang"
        return dict(datev_kategorie=kat, datev_email=DATEV_BOXES[kat],
                    dropbox_ordner=None, zahlungsstatus=zahlungsstatus)
    ordner = {"bank": "XE bezahlte Eingangsrechnungen",
              "kreditkarte_master": "XE bezahlte Eingangsrechnungen/Master",
              "kasse": "XE Kassenbelege",
              "rechnungsausgang": "XE offene Ausgangsrechnugnen"}.get(kat, "XE offene Eingangsrechnungen")
    return dict(datev_kategorie=None, datev_email=None, dropbox_ordner=ordner,
                zahlungsstatus=zahlungsstatus)


_AMOUNT_RE = r'\d{1,3}(?:\.\d{3})*,\d{2}'
def _amount_val(s): return float(s.replace(".", "").replace(",", "."))

def extract_total(t):
    """Rechnungs-Endbetrag bevorzugt aus einer beschrifteten Summenzeile ziehen
    (Rechnungsbetrag/Gesamtbetrag/Zahlbetrag ...), nur als Notfall max()."""
    labels = [
        r'rechnungsbetrag', r'gesamtbetrag', r'zahlbetrag',
        r'zu\s*zahlender?\s*betrag', r'zu\s*zahlen(?:der)?\s*betrag',
        r'endbetrag', r'rechnungssumme', r'gesamtsumme',
        r'bruttobetrag', r'gesamt\s*brutto', r'\btotal\b',
    ]
    best = None  # (prioritaets-index, betrag) — kleiner index = besser
    for line in t.split("\n"):
        low = line.lower()
        for i, lab in enumerate(labels):
            if re.search(lab, low):
                ams = re.findall(_AMOUNT_RE, line)
                if ams:
                    val = _amount_val(ams[-1])
                    # bei Gleichstand der Prioritaet die spaetere (untere) Zeile nehmen
                    if best is None or i <= best[0]:
                        best = (i, val)
                break
    if best is not None:
        return round(best[1], 2)
    amts = re.findall(_AMOUNT_RE, t)
    if amts:
        return round(max(_amount_val(a) for a in amts), 2)
    return None

def extract_fields(pdf_path):
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            t="\n".join((p.extract_text() or "") for p in pdf.pages)
    except Exception:
        return {}
    out={}
    # Kein Label-Wort als Rechnungsnummer uebernehmen (Tabellenkopf "Rechnungsnr.: Kundennr.: Datum:")
    _bad=re.compile(r'^(kunden|datum|leistung|seite|rechnung|belegn|auftrag)',re.I)
    m=re.search(r'(?:rechnungs\-?\s*(?:nr|nummer)|invoice\s*(?:no|number))[:.\s]*([A-Z0-9][A-Z0-9/\-]{3,})',t,re.I)
    if m and not _bad.match(m.group(1)):
        out["rechnungsnummer"]=m.group(1).strip()
    else:
        # Tabellen-Layout: Labelzeile, Werte erst in der naechsten Zeile
        m2=re.search(r'(?:rechnungs\-?\s*(?:nr|nummer)|invoice\s*(?:no|number))[^\n]*\n\s*([A-Z0-9][A-Z0-9/\-]{3,})',t,re.I)
        if m2 and not _bad.match(m2.group(1)):
            out["rechnungsnummer"]=m2.group(1).strip()
    md=re.search(r'(\d{1,2}\.\s*\d{1,2}\.\s*\d{4}|\d{1,2}\.\s*[A-Za-zäöü]+\s*\d{4}|\d{4}-\d{2}-\d{2})',t)
    val=extract_total(t)
    if val is not None:
        out["betrag_brutto"]=val
    # Rechnungsempfaenger-Firma (fuer geteilte Absender)
    if re.search(r'x-?media\s*event|event\s*gmbh',t,re.I): out["_empf"]="event"
    elif re.search(r'x-?media\s*music|music\s*gmbh',t,re.I): out["_empf"]="music"
    return out

def ist_rechnung(pdf_path, sender, subject):
    try:
        r=subprocess.run([sys.executable,str(S/"ist_rechnung.py"),str(pdf_path),
                          "--sender",sender or "","--subject",subject or ""],
                         capture_output=True,text=True,timeout=60)
        out=r.stdout+r.stderr
        m=re.search(r'\b(RECHNUNG|GRENZFALL|KEINE)\b',out)
        return (m.group(1) if m else "GRENZFALL"), out.strip().splitlines()[0][:120]
    except Exception as e:
        return "GRENZFALL", f"detector-fehler {e}"

def sha(b): return hashlib.sha256(b).hexdigest()

def hash_exists(h):
    st,d=sb("GET",f"/rest/v1/bh_belege?select=id&pdf_hash=eq.{h}")
    return isinstance(d,list) and len(d)>0

def _upload(path,content):
    h={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"application/pdf","x-upsert":"true"}
    r=urllib.request.Request(f"{SB_URL}/storage/v1/object/belege/{urllib.parse.quote(path)}",data=content,method="POST",headers=h)
    try:
        with urllib.request.urlopen(r) as x: return x.status
    except urllib.error.HTTPError as e: return e.code

def pull_box(box, dry, report, from_uid=None, only_uid=None):
    prefix,firma,offensiv=BOXES[box]
    addr=MENV.get(f"{prefix}_ADDRESS",""); pw=MENV.get(f"{prefix}_PASSWORD","")
    if not addr or not pw:
        report.append(f"  {box}: kein Zugang in mail.env — uebersprungen"); return
    cur=cursors(); last=int(cur.get(box,0)) if from_uid is None else int(from_uid)-1
    M=imaplib.IMAP4_SSL(IMAP_HOST,IMAP_PORT); M.login(addr,pw); M.select("INBOX",readonly=True)
    typ,data=M.uid("search",None,"ALL")
    uids=[int(x) for x in data[0].split()]
    if only_uid is not None:                # gezielter Nachlauf fuer genau eine Mail
        new=[u for u in uids if u==int(only_uid)]
    else:
        new=[u for u in uids if u>last]
    report.append(f"  {box} ({addr}): {len(new)} neue Mail(s)")
    maxseen=last
    for u in new:
        maxseen=max(maxseen,u)
        t,d=M.uid("fetch",str(u),"(RFC822)")
        if not d or not d[0]: continue
        msg=email.message_from_bytes(d[0][1])
        frm=dh(msg.get("From","")); subj=dh(msg.get("Subject",""))
        m=re.search(r'<([^>]+)>',frm); femail=(m.group(1) if m else frm).lower()
        try: maildatum=parsedate_to_datetime(msg.get("Date","")).strftime("%Y-%m-%d")
        except Exception: maildatum=datetime.now().strftime("%Y-%m-%d")
        pdfs=[]
        for part in msg.walk():
            fn=part.get_filename()
            if fn and dh(fn).lower().endswith(".pdf"):
                try: pdfs.append((dh(fn),part.get_payload(decode=True)))
                except Exception: pass
        if femail in IGNORE: continue
        # --- Kein PDF im Anhang: Belegmail (Apple, PayPal & Co.) selbst rendern ---
        html_beleg=None
        if not pdfs:
            if "bewirtung" in subj.lower(): continue
            try:
                body=h2p.mail_body_text(msg)
                treffer=h2p.erkenne_beleg(femail,subj,body)
            except Exception as e:
                report.append(f"    · {subj[:40]} — HTML-Beleg-Pruefung fehlgeschlagen ({e})"); continue
            if not treffer: continue
            gname=h2p.dateiname(treffer,maildatum)
            gpath=WORK/f"{box}_{u}_{gname}"
            content=h2p.beleg_pdf(gpath,treffer=treffer,absender=frm,betreff=subj,
                                  mail_datum=maildatum,empfaenger=addr,body_text=body)
            html_beleg=dict(treffer=treffer,hash=h2p.beleg_hash(femail,subj,body))
            pdfs=[(gname,content)]
        if not pdfs: continue
        # Merge bekannte Mehrfach-PDF-Absender
        mergekey=next((k for k in MERGE_SENDER if k in (frm+" "+femail).lower()),None)
        groups=[]
        if mergekey and len(pdfs)>1:
            order=MERGE_SENDER[mergekey]
            ordered=sorted(pdfs,key=lambda p: next((i for i,o in enumerate(order) if o.lower() in p[0].lower()),9))
            groups.append(("merge",ordered))
        else:
            groups=[("single",[p]) for p in pdfs]
        for kind,grp in groups:
            merge_rgnr=None
            # PDF materialisieren (ggf. mergen)
            if kind=="merge":
                from pypdf import PdfWriter,PdfReader
                import io
                w=PdfWriter()
                for _,content in grp:
                    for pg in PdfReader(io.BytesIO(content)).pages: w.add_page(pg)
                buf=io.BytesIO(); w.write(buf); content=buf.getvalue()
                fname=f"{mergekey.upper()}_{u}.pdf"
                # UTA: Rechnungsnummer aus dem RE-Dateinamen ziehen (…_RE_..._<Nr>.pdf) -> Dedup
                merge_rgnr=None
                for pfn,_ in grp:
                    mm=re.search(r'_RE_.*?_(\d{6,})', pfn) or re.search(r'(\d{7,})', pfn)
                    if mm: merge_rgnr=mm.group(1); break
            else:
                fname,content=grp[0]
            tmp=WORK/f"{box}_{u}_{re.sub(r'[^A-Za-z0-9._-]','_',fname)[:60]}"
            tmp.write_bytes(content)
            # HTML-Beleg: stabiler Hash aus dem Mailinhalt (PDF-Bytes enthalten die Uhrzeit)
            h=html_beleg["hash"] if html_beleg else sha(content)
            if hash_exists(h):
                report.append(f"    · {subj[:40]} — Dedup (schon im Bestand)"); continue
            if "bewirtung" in subj.lower():
                report.append(f"    · {subj[:40]} — Bewirtungsbeleg -> eigener Workflow (bewirtung.py), uebersprungen"); continue
            if html_beleg:
                verdict="HTML-BELEG"
            else:
                verdict,vline=ist_rechnung(tmp,femail,subj)
                if verdict=="KEINE" or (not offensiv and verdict!="RECHNUNG"):
                    report.append(f"    · {subj[:40]} — {verdict}, uebersprungen ({box})"); continue
            route=match_route(frm,femail)
            if html_beleg:
                tr=html_beleg["treffer"]
                fields=dict(betrag_brutto=tr.get("betrag"),rechnungsnummer=tr.get("nummer"))
                eff_firma=firma
                boxinfo=(box_from_route(route,eff_firma) if route
                         else box_from_kategorie(tr.get("zielbox"),eff_firma,tr.get("zahlweg")))
            else:
                fields=extract_fields(tmp)
                eff_firma = fields.get("_empf") or firma
                boxinfo=box_from_route(route,eff_firma)
            rgnr=merge_rgnr or fields.get("rechnungsnummer")
            if rgnr_exists(rgnr, eff_firma):
                report.append(f"    · {subj[:40]} — Dedup (RgNr {rgnr} schon im Bestand)"); continue
            store=f"eingang/{datetime.now():%Y-%m}/{box}_{u}_{re.sub(r'[^A-Za-z0-9]','',(rgnr or fname))[:30]}.pdf"
            tr=html_beleg["treffer"] if html_beleg else None
            row=dict(firma=eff_firma,typ="tankbeleg" if mergekey=="uta" else "eingangsrechnung",
                     status="warte_bestaetigung",eingangskanal=addr,
                     # Immer der ECHTE Mail-Absender (nie der Routing-Name — sonst steht
                     # bei einem Fehlmatch ein fremder Mensch auf dem Beleg, 31.08.2026).
                     # Der Routing-Treffer steht in ki_ergebnis.route + in den Notizen.
                     absender_name=(frm or (tr.get("absender") if tr else "")
                                    or (route.get("Rechnungssteller").split("(")[0].strip() if route else ""))[:80],
                     absender_email=femail,rechnungsnummer=rgnr,betrag_brutto=fields.get("betrag_brutto"),
                     rechnungsdatum=(tr.get("datum") if tr else None),
                     pdf_dateiname_original=fname,
                     pdf_storage_path=store,pdf_hash=h,
                     ki_konfidenz=(0.95 if route else (0.8 if tr else 0.4)),
                     notizen=f"HUB-INGEST {box} UID{u} {datetime.now():%Y-%m-%d %H:%M}. Detektor:{verdict}."
                             + (f" PDF vom Hub aus der {tr['quelle']}-Belegmail erzeugt"
                                f" (kein PDF-Anhang), Zahlweg {tr.get('zahlweg')}."
                                f" Original: Mail vom {maildatum} in {addr}." if tr else "")
                             + ("" if (route or tr) else " Absender UNBEKANNT — Box bitte in der App waehlen."),
                     ki_ergebnis=dict(quelle=("hub-ingest-html" if tr else "hub-ingest"),
                                      postfach=box,detektor=verdict,
                                      route=(route.get("Rechnungssteller") if route else None),
                                      html_regel=(tr.get("quelle") if tr else None),
                                      zahlweg=(tr.get("zahlweg") if tr else None),
                                      box=boxinfo.get("datev_kategorie") or boxinfo.get("dropbox_ordner")))
            row.update(boxinfo)
            # UTA stehende Freigabe -> autonom freigeben
            if mergekey=="uta":
                row["dirk_entscheidung"]="freigegeben"; row["dirk_entschieden_am"]=datetime.now(timezone.utc).isoformat()
            tag = "AUTO-FREIGABE" if mergekey=="uta" else ("Wartend (HTML-Beleg)" if html_beleg else "Wartend")
            if dry:
                report.append(f"    ✎ [DRY] {eff_firma} | {row['absender_name'][:28]:28} | {row.get('betrag_brutto')} € | {row.get('datev_kategorie') or row.get('dropbox_ordner')} | {tag}")
            else:
                us=_upload(store,content)
                st,b=sb("POST","/rest/v1/bh_belege",data=row)
                ok = isinstance(b,list)
                report.append(f"    ✓ {eff_firma} | {row['absender_name'][:28]:28} | {row.get('betrag_brutto')} € | {row.get('datev_kategorie') or row.get('dropbox_ordner')} | {tag} | storage={us} db={st}")
    M.logout()
    if not dry:
        cur=cursors()                       # Cursor nie zurueckdrehen (--from-uid-Nachlauf)
        cur[box]=max(maxseen,int(cur.get(box,0))); save_cursors(cur)

def main():
    dry="--dry-run" in sys.argv
    only=None; from_uid=None; only_uid=None
    if "--box" in sys.argv: only=sys.argv[sys.argv.index("--box")+1]
    if "--from-uid" in sys.argv: from_uid=sys.argv[sys.argv.index("--from-uid")+1]
    if "--only-uid" in sys.argv: only_uid=sys.argv[sys.argv.index("--only-uid")+1]
    report=[f"bh_ingest {datetime.now():%Y-%m-%d %H:%M}{' (DRY-RUN)' if dry else ''}"]
    for box in (["rechnung","info","rechnung_event","info_event"] if not only else [only]):
        try: pull_box(box,dry,report,from_uid=(from_uid if only else None),
                      only_uid=(only_uid if only else None))
        except Exception as e: report.append(f"  {box}: FEHLER {e}")
    print("\n".join(report))

if __name__=="__main__":
    main()
