#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
_hubpaths.py — portable Pfad-Erkennung für alle recall-Werkzeuge.

Damit laufen recall/memory_index/journal/feedback IDENTISCH im eigenen Hub UND
in jedem verschenkten Mantel — ohne harte, owner-spezifische Pfade (die wären
(a) ein Daten-Leck im Mantel und (b) ein Ausfallrisiko, wenn ein Pfad wegfällt).

hub_root():  die Hub-Wurzel (Ordner mit .claude/ + scripts/).
memory_dir(): der Memory-Ordner — erkennt beide Konventionen:
   - Mantel/self-contained:  <hub>/memory
   - Claude-Code-Auto-Memory: ~/.claude/projects/<slug>/memory
"""
import os, re, glob

def hub_root():
    here = os.path.dirname(os.path.abspath(__file__))          # <hub>/scripts/recall
    cand = os.path.abspath(os.path.join(here, "..", ".."))     # <hub>
    for p in (cand, os.getcwd()):
        if os.path.isdir(os.path.join(p, ".claude")) or os.path.isdir(os.path.join(p, "scripts")):
            return p
    return cand

def memory_dir(hub=None):
    hub = hub or hub_root()
    home = os.path.expanduser("~")
    # Claude-Code-Slug: Laufwerks-/Pfadtrenner + Unterstrich → Bindestrich
    slug = re.sub(r"[:\\/_]", "-", hub)
    cands = [
        os.path.join(hub, "memory"),                                   # self-contained (Mantel)
        os.path.join(home, ".claude", "projects", slug, "memory"),     # abgeleiteter Slug
    ]
    # Fallback: irgendein projects/*/memory, das nach diesem Hub aussieht
    base = os.path.basename(hub).lower()
    for g in sorted(glob.glob(os.path.join(home, ".claude", "projects", "*", "memory"))):
        if base in g.lower():
            cands.append(g)
    for g in sorted(glob.glob(os.path.join(home, ".claude", "projects", "*", "memory"))):
        cands.append(g)                                                # letzter Fallback: erster Treffer
    for c in cands:
        if os.path.isdir(c):
            return c
    return os.path.join(hub, "memory")     # Default = Mantel-Konvention
