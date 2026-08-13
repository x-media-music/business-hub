#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
journal.py — Ereignis-Journal: bewahrt die episodische Historie („was ist wann passiert").

Problem: `logs/letzter_chat.md` (die kuratierte Tages-Übergabe) wird jede Session
ÜBERSCHRIEBEN → der beste Tagesabschluss ging bisher verloren.

Dieses Script:
  1. snapshot  — kopiert die aktuelle letzter_chat.md nach
                 logs/archiv/letzter_chat_<Datum>.md (append-only, nie überschrieben).
  2. build     — baut logs/ereignis_journal.md: eine chronologische, durchsuchbare
                 Zeitleiste aller archivierten Übergaben + Session-Protokolle.

Beides idempotent. Beim „Ende"-Befehl aufrufen:
  python scripts/recall/journal.py            # = snapshot + build
Die Historie ist danach über recall.py voll durchsuchbar (recall indexiert logs/archiv).
"""
import os, re, sys, time, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _hubpaths import hub_root

HUB = hub_root()
LOGS = os.path.join(HUB, "logs")
ARCHIV = os.path.join(LOGS, "archiv")
LETZTER = os.path.join(LOGS, "letzter_chat.md")
JOURNAL = os.path.join(LOGS, "ereignis_journal.md")

def _read(p):
    try:
        with open(p, encoding="utf-8", errors="ignore") as f: return f.read()
    except Exception: return ""

def _date_of(path):
    """Datum aus Dateiname (YYYY-MM-DD) oder mtime."""
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", os.path.basename(path))
    if m: return m.group(0)
    return time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(path)))

def snapshot():
    """letzter_chat.md dauerhaft ins Archiv sichern (vor dem nächsten Überschreiben)."""
    if not os.path.isfile(LETZTER):
        print("keine letzter_chat.md — nichts zu sichern"); return
    os.makedirs(ARCHIV, exist_ok=True)
    d = _date_of(LETZTER)
    dst = os.path.join(ARCHIV, f"letzter_chat_{d}.md")
    new = _read(LETZTER)
    if os.path.isfile(dst):
        if hashlib.md5(_read(dst).encode()).hexdigest() == hashlib.md5(new.encode()).hexdigest():
            print(f"Übergabe {d} bereits identisch archiviert — ok"); return
        # gleicher Tag, anderer Inhalt → mit Zeitstempel danebenlegen (nie überschreiben)
        dst = os.path.join(ARCHIV, f"letzter_chat_{d}_{time.strftime('%H%M%S')}.md")
    with open(dst, "w", encoding="utf-8") as f: f.write(new)
    print(f"Übergabe archiviert: archiv/{os.path.basename(dst)}")

def _teaser(text, n=180):
    for ln in text.splitlines():
        s = ln.strip().lstrip("#>*-• ").strip()
        if len(s) > 15 and not s.startswith("---"):
            s = re.sub(r"\s+", " ", s)
            return (s[:n] + "…") if len(s) > n else s
    return "(kein Text)"

def build():
    """Chronologische Zeitleiste aus allen archivierten Übergaben + Protokollen."""
    os.makedirs(ARCHIV, exist_ok=True)
    items = []
    for fn in os.listdir(ARCHIV):
        if not fn.endswith(".md"): continue
        if not (fn.startswith("letzter_chat_") or fn.startswith("session_protokoll_")):
            continue
        p = os.path.join(ARCHIV, fn)
        kind = "Übergabe" if fn.startswith("letzter_chat_") else "Protokoll"
        items.append((_date_of(p), kind, fn, _teaser(_read(p))))
    # aktuellster Tag zuerst
    items.sort(key=lambda x: (x[0], x[1]), reverse=True)

    out = ["# 🗓️  Ereignis-Journal — was ist wann passiert",
           f"> Generiert {time.strftime('%d.%m.%Y %H:%M')} von `scripts/recall/journal.py` · "
           f"append-only Historie · Volltext: `python scripts/recall/recall.py \"<frage>\"`",
           f"> {len(items)} Einträge. Übergaben = kuratierter Tagesabschluss, Protokolle = Stichwort-Mitschrift.\n"]
    cur = None
    for d, kind, fn, teaser in items:
        if d != cur:
            out.append(f"\n## {d}"); cur = d
        out.append(f"- **{kind}** · `archiv/{fn}` — {teaser}")
    with open(JOURNAL, "w", encoding="utf-8") as f: f.write("\n".join(out) + "\n")
    print(f"ereignis_journal.md gebaut: {len(items)} Einträge")

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("snapshot", "all"): snapshot()
    if mode in ("build", "all"):    build()

if __name__ == "__main__":
    main()
