#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
memory_index.py (generisch) — erzeugt MEMORY.md als THEMATISCHEN REGISTER-INDEX.

Prinzip (Leitz-Ordner): jede Merkdatei bleibt VOLL erhalten, nur das
Inhaltsverzeichnis wird nach Register gruppiert. Der Index wird aus dem
DATEISYSTEM erzeugt → es kann keine verwaiste Datei mehr geben.

- Kuratierte Hooks/Titel aus der bestehenden MEMORY.md werden BEWAHRT.
- Neue/verwaiste Dateien bekommen Titel+Hook aus dem Frontmatter (name/description).
- Nicht sicher zuordenbare Dateien landen sichtbar unter „📌 Sonstiges" (nie verloren).
- Hooks werden gekappt (voller Text bleibt in der Datei) → MEMORY.md bleibt klein.

Aufruf:
  python scripts/recall/memory_index.py            # schreibt MEMORY.md (Backup vorher)
  python scripts/recall/memory_index.py --dry-run  # nur anzeigen, nichts schreiben
"""
import os, re, sys, io, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _hubpaths import memory_dir

MEMDIR = memory_dir()
MEMORY = os.path.join(MEMDIR, "MEMORY.md")

# ---- Register in Anzeige-Reihenfolge. (schluessel, Überschrift) --------------
# Neutral gehalten — passe die Überschriften/Stichworte an deine Themen an.
REGISTERS = [
    ("arbeitsweise", "✍️  Arbeitsweise & Grundregeln"),
    ("email",        "📧  E-Mail & Versand"),
    ("system",       "⚙️  System · Technik · Sync · Session"),
    ("projekte",     "🗂️  Projekte & Vorgänge"),
    ("kontakte",     "📇  Kontakte & Referenzen"),
    ("sonstiges",    "📌  Sonstiges (bitte einsortieren)"),
]

# ---- Klassifikation: ERSTE passende Regel gewinnt. Reihenfolge = Priorität. --
# Generisch, data-frei. Ergänze eigene Stichworte je Register.
RULES = [
    ("email",        ["mail", "versand", "gate", "brief", "anrede", "signatur", "html", "bcc"]),
    ("system",       ["script", "token", "sync", "system", "session", "backup", "index",
                      "recall", "chrome", "hook", "outlook", "resilienz", "cwd", "inbox",
                      "wenn_dann", "journal", "feedback_loop"]),
]

def classify(fname, title, hook):
    # Prefix-Konventionen zuerst (Claude-Code-Merkdateien).
    if fname.startswith("reference_"):
        pref = "kontakte"
    elif fname.startswith("project_"):
        pref = "projekte"
    else:
        pref = None
    blob = (fname + " " + title + " " + hook).lower()
    for reg, kws in RULES:
        for kw in kws:
            if kw in blob:
                return reg
    if pref:
        return pref
    if fname.startswith("feedback_"):
        return "arbeitsweise"
    return "sonstiges"

def parse_existing(path):
    """filename -> (title, hook) aus bestehender MEMORY.md (kuratierte Hooks bewahren)."""
    out = {}
    if not os.path.isfile(path):
        return out
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.match(r"\s*-\s*\[(.+?)\]\(([^)]+\.md)\)\s*[—-]+\s*(.*)", line)
            if m:
                title = m.group(1).strip()
                fn = os.path.basename(m.group(2).strip())
                hook = m.group(3).strip()
                out[fn] = (title, hook)
    return out

def frontmatter(path):
    name = desc = ""
    with open(path, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    m = re.search(r"^name:\s*(.+)$", text, re.M)
    if m: name = m.group(1).strip()
    m = re.search(r"^description:\s*(.+)$", text, re.M)
    if m: desc = m.group(1).strip().strip('"')
    if not name:
        m = re.search(r"^#\s+(.+)$", text, re.M)
        if m: name = m.group(1).strip()
    return name, desc

HOOK_MAX = 60   # Kappung der Index-Hooks — haelt MEMORY.md klein. Voller Text
TITLE_MAX = 60  # steht in der jeweiligen Datei; der Index ist nur Wegweiser.

def _cap(text, n):
    """Text auf n Zeichen an Wortgrenze kuerzen, '…' anhaengen wenn gekuerzt."""
    h = (text or "").strip()
    if len(h) <= n:
        return h
    core = h[:n].rstrip("… ")
    cut = core.rsplit(" ", 1)[0].rstrip(" ,;:—-") if " " in core else core
    return cut + "…"

def build():
    curated = parse_existing(MEMORY)
    files = [f for f in os.listdir(MEMDIR) if f.endswith(".md") and f != "MEMORY.md"]
    files.sort()
    buckets = {k: [] for k, _ in REGISTERS}
    orphans_added = []
    for fn in files:
        path = os.path.join(MEMDIR, fn)
        name, desc = frontmatter(path)
        ctitle, chook = curated.get(fn, (None, None))
        # Titel: kuratierter (huebscher) Titel hat Vorrang, sonst Frontmatter-Name.
        title = ctitle or name or fn[:-3]
        # Hook: volle description hat Vorrang (deterministisch kappbar), sonst
        # kuratierter Hook aus MEMORY.md, sonst Platzhalter.
        hook = desc or chook or "(neu indexiert — Hook ergänzen)"
        if fn not in curated:
            orphans_added.append(fn)
        reg = classify(fn, title, hook)
        buckets[reg].append((title, fn, hook))
    for k in buckets:
        buckets[k].sort(key=lambda x: x[0].lower())
    return buckets, orphans_added, len(files)

def render(buckets, total):
    ts = time.strftime("%d.%m.%Y %H:%M")
    out = io.StringIO()
    out.write(f"# 🧠 MEMORY — Register-Index ({total} Merkdateien)\n")
    out.write(f"> Generiert {ts} von `scripts/recall/memory_index.py` · thematisch gruppiert, "
              f"0 % Wissensverlust · Hooks gekappt (voll in Datei) · "
              f"Suche: `python scripts/recall/recall.py \"<frage>\"`\n\n")
    for key, heading in REGISTERS:
        rows = buckets.get(key, [])
        if not rows:
            continue
        out.write(f"## {heading}  ({len(rows)})\n")
        for title, fn, hook in rows:
            out.write(f"- [{_cap(title, TITLE_MAX)}]({fn}) — {_cap(hook, HOOK_MAX)}\n")
        out.write("\n")
    return out.getvalue()

def main():
    dry = "--dry-run" in sys.argv
    buckets, orphans, total = build()
    content = render(buckets, total)
    counts = " · ".join(f"{k}:{len(buckets[k])}" for k, _ in REGISTERS if buckets[k])
    print(f"Register: {counts}")
    if orphans:
        print(f"Neu in Index aufgenommen ({len(orphans)} vorher verwaist): " + ", ".join(orphans))
    if dry:
        print("\n----- DRY-RUN, MEMORY.md NICHT geschrieben -----\n")
        print(content)
        return
    if os.path.isfile(MEMORY):
        bak = MEMORY + ".bak_" + time.strftime("%Y%m%d_%H%M%S")
        with open(MEMORY, encoding="utf-8", errors="ignore") as f: old = f.read()
        with open(bak, "w", encoding="utf-8") as f: f.write(old)
        print(f"Backup: {os.path.basename(bak)}")
    with open(MEMORY, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"MEMORY.md neu geschrieben ({total} Einträge, gruppiert).")

if __name__ == "__main__":
    main()
