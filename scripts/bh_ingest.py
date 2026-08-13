#!/usr/bin/env python3
"""
bh_ingest.py — Hub-Ingest fuer die Buchhaltung (Hub fuehrt, App = Anzeige+Freigabe).

Zieht die 4 Postfaecher inkrementell, erkennt Rechnungen (ist_rechnung.py),
routet ueber datev_routing.csv, merged bekannte Mehrfach-PDF-Absender (UTA),
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
"""
from __future__ import annotations
import os, sys, re, json, ssl, imaplib, email, hashlib, subprocess, urllib.request, urllib.parse, csv
from email.header import decode_header, make_header
from datetime import datetime, timezone
from pathlib import Path

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
def match_route(absender_name, absender_email):
    """Streng: matcht nur, wenn ein distinktives Token (>=4 Zeichen, nicht generisch)
    des Rechnungsstellers im Absender vorkommt. Verhindert Fehltreffer wie 'ts'->'events'."""
    hay=f"{absender_name} {absender_email}".lower()
    for r in ROUTES:
        rn=(r.get("Rechnungssteller") or "").split("(")[0].lower()
        toks=[w for w in re.findall(r"[a-zäöüß0-9]{4,}",rn) if w not in GENERIC]
        if toks and any(t in hay for t in toks):
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

def extract_fields(pdf_path):
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            t="\n".join((p.extract_text() or "") for p in pdf.pages)
    except Exception:
        return {}
    out={}
    m=re.search(r'(?:rechnungs\-?\s*(?:nr|nummer)|invoice\s*(?:no|number))[:.\s]*([A-Z0-9][A-Z0-9/\-]{3,})',t,re.I)
    if m: out["rechnungsnummer"]=m.group(1).strip()
    md=re.search(r'(\d{1,2}\.\s*\d{1,2}\.\s*\d{4}|\d{1,2}\.\s*[A-Za-zäöü]+\s*\d{4}|\d{4}-\d{2}-\d{2})',t)
    amts=re.findall(r'\d{1,3}(?:\.\d{3})*,\d{2}',t)
    if amts:
        val=max(float(a.replace(".","").replace(",",".")) for a in amts)
        out["betrag_brutto"]=round(val,2)
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

def pull_box(box, dry, report):
    prefix,firma,offensiv=BOXES[box]
    addr=MENV.get(f"{prefix}_ADDRESS",""); pw=MENV.get(f"{prefix}_PASSWORD","")
    if not addr or not pw:
        report.append(f"  {box}: kein Zugang in mail.env — uebersprungen"); return
    cur=cursors(); last=int(cur.get(box,0))
    M=imaplib.IMAP4_SSL(IMAP_HOST,IMAP_PORT); M.login(addr,pw); M.select("INBOX",readonly=True)
    typ,data=M.uid("search",None,"ALL")
    uids=[int(x) for x in data[0].split()]
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
        pdfs=[]
        for part in msg.walk():
            fn=part.get_filename()
            if fn and dh(fn).lower().endswith(".pdf"):
                try: pdfs.append((dh(fn),part.get_payload(decode=True)))
                except Exception: pass
        if not pdfs: continue
        if femail in IGNORE: continue
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
            h=sha(content)
            if hash_exists(h):
                report.append(f"    · {subj[:40]} — Dedup (schon im Bestand)"); continue
            if "bewirtung" in subj.lower():
                report.append(f"    · {subj[:40]} — Bewirtungsbeleg -> eigener Workflow (bewirtung.py), uebersprungen"); continue
            verdict,vline=ist_rechnung(tmp,femail,subj)
            if verdict=="KEINE" or (not offensiv and verdict!="RECHNUNG"):
                report.append(f"    · {subj[:40]} — {verdict}, uebersprungen ({box})"); continue
            route=match_route(frm,femail)
            fields=extract_fields(tmp)
            eff_firma = fields.get("_empf") or firma
            boxinfo=box_from_route(route,eff_firma)
            rgnr=merge_rgnr or fields.get("rechnungsnummer")
            if rgnr_exists(rgnr, eff_firma):
                report.append(f"    · {subj[:40]} — Dedup (RgNr {rgnr} schon im Bestand)"); continue
            store=f"eingang/{datetime.now():%Y-%m}/{box}_{u}_{re.sub(r'[^A-Za-z0-9]','',(rgnr or fname))[:30]}.pdf"
            row=dict(firma=eff_firma,typ="tankbeleg" if mergekey=="uta" else "eingangsrechnung",
                     status="warte_bestaetigung",eingangskanal=addr,
                     absender_name=(route.get("Rechnungssteller").split("(")[0].strip() if route else frm[:80]),
                     absender_email=femail,rechnungsnummer=rgnr,betrag_brutto=fields.get("betrag_brutto"),
                     pdf_storage_path=store,pdf_hash=h,ki_konfidenz=(0.95 if route else 0.4),
                     notizen=f"HUB-INGEST {box} UID{u} {datetime.now():%Y-%m-%d %H:%M}. Detektor:{verdict}."
                             + ("" if route else " Absender UNBEKANNT — Box bitte in der App waehlen."),
                     ki_ergebnis=dict(quelle="hub-ingest",postfach=box,detektor=verdict,
                                      route=(route.get("Rechnungssteller") if route else None),
                                      box=boxinfo.get("datev_kategorie") or boxinfo.get("dropbox_ordner")))
            row.update(boxinfo)
            # UTA stehende Freigabe -> autonom freigeben
            if mergekey=="uta":
                row["dirk_entscheidung"]="freigegeben"; row["dirk_entschieden_am"]=datetime.now(timezone.utc).isoformat()
            tag = "AUTO-FREIGABE" if mergekey=="uta" else "Wartend"
            if dry:
                report.append(f"    ✎ [DRY] {eff_firma} | {row['absender_name'][:28]:28} | {row.get('betrag_brutto')} € | {row.get('datev_kategorie') or row.get('dropbox_ordner')} | {tag}")
            else:
                us=_upload(store,content)
                st,b=sb("POST","/rest/v1/bh_belege",data=row)
                ok = isinstance(b,list)
                report.append(f"    ✓ {eff_firma} | {row['absender_name'][:28]:28} | {row.get('betrag_brutto')} € | {row.get('datev_kategorie') or row.get('dropbox_ordner')} | {tag} | storage={us} db={st}")
    M.logout()
    if not dry:
        cur[box]=maxseen; save_cursors(cur)

def main():
    dry="--dry-run" in sys.argv
    only=None
    if "--box" in sys.argv: only=sys.argv[sys.argv.index("--box")+1]
    report=[f"bh_ingest {datetime.now():%Y-%m-%d %H:%M}{' (DRY-RUN)' if dry else ''}"]
    for box in (["rechnung","info","rechnung_event","info_event"] if not only else [only]):
        try: pull_box(box,dry,report)
        except Exception as e: report.append(f"  {box}: FEHLER {e}")
    print("\n".join(report))

if __name__=="__main__":
    main()
