#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tisch-Info-Mails DIE NEUE 107.7 Party Weinstadt-Endersbach 25.07.2026.
Erzeugt pro Empfaenger einen personalisierten HTML-Body aus _template.html.
  --generate  : nur Bodies bauen (Default)
  --send      : nach OWNER-FREIGABE tatsaechlich versenden (send_email.py je Empfaenger)
Absender: Dirk Woehrle persoenlich, Postfach info_event, event-Signatur (Inline-Logo).
"""
import csv, hashlib, subprocess, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
HUB  = BASE.parents[2]                      # business_hub_Dirk_STARTER
CSV  = BASE / "empfaenger.csv"
TPL  = (BASE / "_template.html").read_text(encoding="utf-8")
OUT  = BASE / "out"; OUT.mkdir(exist_ok=True)
SUBJECT = "Ihr Tisch fuer die DIE NEUE 107.7 Party heute Abend in Weinstadt-Endersbach"
LOGO = HUB / "module" / "signaturen" / "logo.png"

def tischsatz(tisch, personen):
    if "+" in tisch:
        return f"Ihre reservierten Tische: <strong>Nr. {tisch}</strong><br><span style=\"font-size:14px;color:#555;\">(ganzer Tisch – {personen} Personen)</span>"
    return f"Ihr reservierter Tisch: <strong>Nr. {tisch}</strong><br><span style=\"font-size:14px;color:#555;\">(Tisch für {personen} Personen)</span>"

def build():
    items=[]
    with open(CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter=";"):
            vn=row["vorname"].strip() or "und herzlich willkommen"
            body=TPL.replace("{VORNAME}", vn).replace("{TISCHSATZ}", tischsatz(row["tisch"].strip(), row["personen"].strip()))
            safe=row["tisch"].replace(" ","").replace("+","-")
            p=OUT / f"tisch_{safe}_{vn}.html"
            p.write_text(body, encoding="utf-8")
            items.append((row["email"].strip(), p, body))
    return items

def main():
    send = "--send" in sys.argv
    items = build()
    print(f"{len(items)} Bodies erzeugt in {OUT}")
    if not send:
        print("Nur generiert. Zum Senden: python3 run_tischmails.py --send")
        return
    ok=0; fail=[]
    for mail, path, body in items:
        h=hashlib.md5(body.encode("utf-8")).hexdigest()
        cmd=["python3", str(HUB/"scripts"/"send_email.py"),
             "--from","info_event","--absender","owner",
             "--to",mail,"--subject",SUBJECT,
             "--body-file",str(path),
             "--inline",f"logo={LOGO}","--gate-hash",h]
        r=subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode==0:
            ok+=1; print(f"  OK   {mail}")
        else:
            fail.append(mail); print(f"  FEHL {mail}: {r.stderr.strip()[:160]}")
    print(f"\nGesendet: {ok}/{len(items)} | Fehler: {len(fail)}")
    if fail: print("Fehlerhafte Empfaenger:", ", ".join(fail))

if __name__=="__main__":
    main()
