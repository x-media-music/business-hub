#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""memory_index.py (generisch) — MEMORY.md als Register-Index, aus dem Dateisystem erzeugt.
Sammelt verwaiste Merkdateien automatisch ein. Aufruf: python scripts/recall/memory_index.py"""
import os, re, sys, io, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _hubpaths import memory_dir

MEMDIR = memory_dir()
MEMORY = os.path.join(MEMDIR, "MEMORY.md")

REGISTERS = [
    ("arbeitsweise", "Arbeitsweise & Grundregeln"),
    ("email",        "E-Mail & Versand"),
    ("system",       "System & Technik"),
    ("kontakte",     "Kontakte & Referenzen"),
    ("projekte",     "Projekte"),
    ("sonstiges",    "Sonstiges"),
]

def reg_of(fn, text):
    low = (fn + " " + text[:400]).lower()
    if fn.startswith("reference_"): return "kontakte"
    if fn.startswith("project_"):   return "projekte"
    if any(k in low for k in ("mail", "versand", "gate", "brief", "anrede", "signatur")): return "email"
    if any(k in low for k in ("script", "token", "sync", "system", "session", "backup", "index", "recall")): return "system"
    if fn.startswith("feedback_"):  return "arbeitsweise"
    return "sonstiges"

def meta(p):
    t = open(p, encoding="utf-8", errors="ignore").read()
    n = re.search(r"^name:\s*(.+)$", t, re.M)
    d = re.search(r"^description:\s*(.+)$", t, re.M)
    h = re.search(r"^#\s+(.+)$", t, re.M)
    title = n.group(1).strip() if n else (h.group(1).strip() if h else os.path.basename(p)[:-3])
    desc = d.group(1).strip().strip('"') if d else ""
    return title, desc, t

def main():
    files = [f for f in os.listdir(MEMDIR) if f.endswith(".md") and f != "MEMORY.md"]
    b = {k: [] for k, _ in REGISTERS}
    for f in sorted(files):
        name, desc, t = meta(os.path.join(MEMDIR, f))
        b[reg_of(f, t)].append((name, f, desc))
    out = io.StringIO()
    out.write(f"# MEMORY — Register-Index ({len(files)})\n")
    out.write(f"> {time.strftime('%d.%m.%Y %H:%M')} · Schnellzugriff: python scripts/recall/recall.py \"<frage>\"\n\n")
    for k, head in REGISTERS:
        if not b[k]:
            continue
        out.write(f"## {head} ({len(b[k])})\n")
        for name, f, desc in b[k]:
            out.write(f"- [{name}]({f}) — {desc}\n")
        out.write("\n")
    # Fit-Anpassung x-media: bestehende MEMORY.md vor dem Ueberschreiben sichern
    # (rollierendes Backup; .prev.bak wird von recall/memory_index ignoriert).
    if os.path.isfile(MEMORY):
        try:
            import shutil
            shutil.copy2(MEMORY, MEMORY + ".prev.bak")
        except Exception:
            pass
    open(MEMORY, "w", encoding="utf-8").write(out.getvalue())
    print(f"MEMORY.md: {len(files)} Einträge, gruppiert. (Backup: MEMORY.md.prev.bak)")

if __name__ == "__main__":
    main()
