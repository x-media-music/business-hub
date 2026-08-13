#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
recall.py — EIN Schnellzugriff auf das GESAMTE Wissen des Business Hub.

Sucht in EINEM Aufruf gleichzeitig über alle Wissens-Speicher:
  - Auto-Memory (Regeln/Projekte/Referenzen)
  - Wissensbasis (Kontakte/Orte/Vorgänge A-Z)
  - Logs / Ereignis-Journal (was ist wann passiert)
  - Fallakten in den Modulen (Verträge, Fälle, Projekte, ...)

Rankt die Treffer (Dateiname > Titel/Description > Body, + wieviele
Suchbegriffe getroffen, + Aktualität) und zeigt je Treffer:
  Rang · Score · Speicher · Pfad · bester Snippet.

Aufruf:
  python scripts/recall/recall.py "welcher lieferant für teil x"
  python scripts/recall/recall.py "stand vertrag kunde y" --top 5
  python scripts/recall/recall.py "was war letzte woche" --store logs,wissensbasis

Keine externen Abhängigkeiten. Windows/utf-8-sicher. CWD-aware (C:\ oder G:\).
"""
import os, re, sys, argparse, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _hubpaths import hub_root, memory_dir

# ---------------------------------------------------------------- Speicher-Konfiguration
HUB = hub_root()
MEM = memory_dir(HUB)

STORES = [
    ("memory",      MEM,                              (".md",)),
    ("wissensbasis", os.path.join(HUB, "wissensbasis"), (".md",)),
    ("logs",        os.path.join(HUB, "logs"),         (".md",)),
    ("modul",       os.path.join(HUB, "module"),       (".md", ".txt")),
]

# Ordner, die beim Scan übersprungen werden (Rauschen / Binär / Backups).
# ACHTUNG: `logs/archiv` (Session-Protokolle = Ereignis-Historie) wird NICHT
# übersprungen — nur der Ansicht-Rausch-Ordner `_archiv` und Backups.
SKIP_DIRS = {"_archiv", "backups", "PDF", "pdf", "__pycache__", ".git"}
# Verwaiste/riesige Rausch-Dateinamen die nichts zum Recall beitragen
SKIP_FILE_RE = re.compile(r"\.(bak|tmp)$|\.bak_", re.I)

STOP = set("""
der die das und oder ein eine einer eines dem den des ist sind war waren
für von mit auf aus bei zum zur im in an als auch nicht nur wie was wer wo
wann warum wieso welche welcher welches wird werden wurde hat habe haben
ich du er sie es wir ihr am um so per bzw etc the a an of to and or is
""".split())

# ---------------------------------------------------------------- Hilfen
def tokenize(q):
    toks = re.findall(r"[0-9a-zA-ZäöüÄÖÜß\-]{2,}", q.lower())
    return [t for t in toks if t not in STOP]

def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def parse_meta(text):
    """Titel/Description aus Frontmatter oder erster Überschrift ziehen."""
    name = desc = ""
    m = re.search(r"^name:\s*(.+)$", text, re.M)
    if m: name = m.group(1).strip()
    m = re.search(r"^description:\s*(.+)$", text, re.M)
    if m: desc = m.group(1).strip().strip('"')
    if not name:
        m = re.search(r"^#\s+(.+)$", text, re.M)
        if m: name = m.group(1).strip()
    return name, desc

def days_old(path):
    try:
        return (time.time() - os.path.getmtime(path)) / 86400.0
    except Exception:
        return 9999.0

# ---------------------------------------------------------------- Scoring
def score_file(path, fname, text, terms):
    low = text.lower()
    flow = fname.lower()
    name, desc = parse_meta(text)
    nlow, dlow = name.lower(), desc.lower()

    hit_terms = 0          # wie viele DISTINKTE Suchbegriffe trifft die Datei überhaupt
    score = 0.0
    for t in terms:
        in_name = t in flow or t in nlow
        in_desc = t in dlow
        cnt = low.count(t)
        if cnt == 0 and not in_name:
            continue
        hit_terms += 1
        if in_name: score += 12
        if in_desc: score += 7
        score += min(cnt, 8) * 1.5      # Body-Häufigkeit, gedeckelt

    if hit_terms == 0:
        return 0.0, name, desc, 0

    # Deckungs-Bonus: Datei, die MEHR der Frage abdeckt, gewinnt klar (quadratisch)
    score += (hit_terms ** 2) * 6

    # Aktualitäts-Bonus: neuere Dateien nach oben (löst Hack-vs-Haußmann:
    # die aktuelle Entscheidung ist frischer als die alten Altakten)
    d = days_old(path)
    if   d <= 3:   score += 10
    elif d <= 14:  score += 7
    elif d <= 45:  score += 4
    elif d <= 120: score += 2

    return score, name, desc, hit_terms

def best_snippet(text, terms, width=160):
    lines = text.splitlines()
    best_line, best_hits = "", -1
    for ln in lines:
        l = ln.lower().strip()
        if not l:
            continue
        h = sum(1 for t in terms if t in l)
        if h > best_hits:
            best_hits, best_line = h, ln.strip()
    s = re.sub(r"\s+", " ", best_line)
    return (s[:width] + "…") if len(s) > width else s

# ---------------------------------------------------------------- Suche
def walk_store(label, root, exts):
    if not root or not os.path.isdir(root):
        return
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            if not fn.lower().endswith(exts):
                continue
            if SKIP_FILE_RE.search(fn):
                continue
            yield label, os.path.join(dp, fn), fn

def search(query, stores=None, top=8):
    terms = tokenize(query)
    if not terms:
        return terms, []
    results = []
    for label, root, exts in STORES:
        if stores and label not in stores:
            continue
        for lab, path, fn in walk_store(label, root, exts):
            text = read_text(path)
            if not text:
                continue
            sc, name, desc, hits = score_file(path, fn, text, terms)
            if sc <= 0:
                continue
            results.append((sc, lab, path, name, desc, hits,
                            best_snippet(text, terms)))
    # Fit-Anpassung x-media: die Haupt-MEMORY.md im Hub-Root mitdurchsuchen
    # (Live-Stand des Hubs; liegt NICHT im memory/-Unterordner, wurde sonst uebersehen).
    if (not stores) or ("memory" in stores):
        root_mem = os.path.join(HUB, "MEMORY.md")
        if os.path.isfile(root_mem):
            rtext = read_text(root_mem)
            if rtext:
                rsc, rname, rdesc, rhits = score_file(root_mem, "MEMORY.md", rtext, terms)
                if rsc > 0:
                    results.append((rsc, "memory", root_mem,
                                    rname or "MEMORY (Hub-Stand)", rdesc, rhits,
                                    best_snippet(rtext, terms)))
    results.sort(key=lambda r: r[0], reverse=True)
    return terms, results[:top]

# ---------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser(description="Schnellzugriff auf das gesamte Hub-Wissen")
    ap.add_argument("query", nargs="+", help="Frage oder Stichworte")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--store", default="", help="Filter: memory,wissensbasis,logs,modul")
    args = ap.parse_args()

    query = " ".join(args.query)
    stores = set(s.strip() for s in args.store.split(",") if s.strip()) or None
    terms, hits = search(query, stores, args.top)

    print(f"\n🔎 RECALL: „{query}\"   (Begriffe: {', '.join(terms) or '—'})")
    print("=" * 72)
    if not hits:
        print("Keine Treffer. Anderes Stichwort? Speicher via --store einschränken?")
        return
    icon = {"memory": "🧠", "wissensbasis": "📚", "logs": "🗓️", "modul": "📁"}
    for i, (sc, lab, path, name, desc, ht, snip) in enumerate(hits, 1):
        title = name or os.path.basename(path)
        rel = path.replace(HUB + os.sep, "").replace(os.sep, "/") if path.startswith(HUB) else path
        print(f"\n{i}. {icon.get(lab,'•')} [{lab}]  {title}   (Score {sc:.0f} · {ht} Begriff/e)")
        print(f"   {rel}")
        if desc:
            print(f"   › {desc[:150]}")
        print(f"   » {snip}")
    print("\n" + "=" * 72)
    print("Öffne den passenden Pfad für die volle Quelle. (Regel: Quelle lesen, nie raten.)")

if __name__ == "__main__":
    main()
