# -*- coding: utf-8 -*-
r"""
audit_hub.py (generisch) — Deterministischer Verdrahtungs-Check deines Hubs.

Zweck: reproduzierbarer "gleicher Test" (Runde 1 vs Runde 2 nach Fixes) für die
`/systemcheck`-Runde. Prüft mechanisch, ob die Strippen richtig liegen — und
leitet ALLES aus dem AKTUELLEN Dateisystem + deinen Regeln ab (keine
eingefrorene, owner-spezifische Liste, die verrotten könnte).

Prüft:
  A. py_compile aller Python-Dateien (scripts/ + module/)
  D. SessionStart/UserPromptSubmit-Hook-Scripts existieren (.claude/settings.json)
  E. JSON-State-Dateien (logs/*.json, backups/*.json) sind valides JSON
  H. Memory-Index-Konsistenz (Dateizahl vs MEMORY.md, Orphans)
  I. Tote Script-Verweise (.py/.cmd/.bat) in .claude/rules + CLAUDE.md
  J. Tote Memory-Referenzen (feedback_/reference_/project_/user_) in Regeln/CLAUDE.md

Read-only. Ändert nichts. Exit 0 = alles grün, 1 = mind. ein FAIL.
"""
import sys, re, json, subprocess
from pathlib import Path

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent.parent   # <hub>
SCRIPTS = ROOT / "scripts"
MODULE = ROOT / "module"

# Memory-Ordner portabel bestimmen (self-contained Mantel ODER Auto-Memory-Slug).
sys.path.insert(0, str(SCRIPTS / "recall"))
try:
    from _hubpaths import memory_dir
    MEMDIR = Path(memory_dir())
except Exception:
    MEMDIR = ROOT / "memory"

results = []   # (severity, text)  severity: OK / WARN / FAIL


def rec(ok, text, warn_only=False):
    sev = "OK" if ok else ("WARN" if warn_only else "FAIL")
    results.append((sev, text))
    mark = "OK  " if ok else ("WARN" if warn_only else "FAIL")
    print(f"  [{mark}] {text}")


def section(name):
    print(f"\n=== {name} ===")


# ---------- A. py_compile ----------
section("A. py_compile alle Python-Dateien")
py_files = list(SCRIPTS.rglob("*.py")) if SCRIPTS.is_dir() else []
if MODULE.is_dir():
    py_files += list(MODULE.rglob("*.py"))
fails = []
for f in py_files:
    r = subprocess.run([sys.executable, "-m", "py_compile", str(f)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        fails.append((f, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "?"))
rec(not fails, f"{len(py_files)} Dateien, {len(fails)} Compile-Fehler")
for f, err in fails:
    rec(False, f"   COMPILE-FEHLER {f.relative_to(ROOT)}: {err}")


# ---------- D. Hook-Scripts aus settings.json ----------
section("D. Hook-Scripts (.claude/settings.json)")
st_path = ROOT / ".claude" / "settings.json"
if not st_path.exists():
    rec(True, ".claude/settings.json nicht vorhanden — ok (keine Hooks)")
else:
    try:
        st = json.loads(st_path.read_text(encoding="utf-8"))
        hook_scripts = re.findall(r"scripts/[\w/]+\.(?:py|cmd|bat)", json.dumps(st))
        if not hook_scripts:
            rec(True, "keine Hook-Scripts referenziert")
        for hs in sorted(set(hook_scripts)):
            rec((ROOT / hs).exists(), f"Hook → {hs}")
    except Exception as e:
        rec(False, f"settings.json nicht lesbar: {e}")


# ---------- E. JSON-State valide ----------
section("E. JSON-State-Dateien valide")
json_state = []
for sub in ("logs", "backups"):
    d = ROOT / sub
    if d.is_dir():
        json_state += sorted(d.glob("*.json"))
if not json_state:
    rec(True, "keine JSON-State-Dateien gefunden (ok)")
for p in json_state:
    try:
        json.loads(p.read_text(encoding="utf-8"))
        rec(True, f"{p.relative_to(ROOT)} valide")
    except Exception as e:
        rec(False, f"{p.relative_to(ROOT)} KAPUTT: {e}")


# ---------- H. Memory-Index-Konsistenz ----------
section("H. Memory-Index-Konsistenz")
try:
    if not MEMDIR.is_dir():
        rec(True, f"Memory-Ordner (noch) nicht vorhanden ({MEMDIR}) — ok bei leerem Hub", warn_only=False)
    else:
        mem_files = [p for p in MEMDIR.glob("*.md") if p.name != "MEMORY.md"]
        idx_path = MEMDIR / "MEMORY.md"
        if not idx_path.exists():
            rec(len(mem_files) == 0, f"MEMORY.md fehlt, aber {len(mem_files)} Merkdateien vorhanden"
                if mem_files else "MEMORY.md fehlt (noch keine Merkdateien — ok)",
                warn_only=bool(mem_files))
        else:
            idx = idx_path.read_text(encoding="utf-8", errors="replace")
            linked = set(re.findall(r"\]\(([\w\-]+\.md)\)", idx))
            orphans = [p.name for p in mem_files if p.name not in linked]
            rec(True, f"{len(mem_files)} Merkdateien, {len(linked)} im Index verlinkt")
            rec(len(orphans) == 0, f"{len(orphans)} nicht im Index verlinkte Memory-Dateien"
                + (f": {orphans[:8]}" if orphans else "")
                + ("  → memory_index.py laufen lassen" if orphans else ""),
                warn_only=bool(orphans))
except Exception as e:
    rec(False, f"Memory-Index-Check Fehler: {e}")


# ---------- I + J. Tote Verweise in Regeln/CLAUDE.md ----------
ref_files = [ROOT / "CLAUDE.md"] + sorted((ROOT / ".claude" / "rules").glob("*.md"))
ref_files = [p for p in ref_files if p.exists()]

section("I. Tote Script-Verweise (.py/.cmd/.bat) in Regeln/CLAUDE.md")
pat = re.compile(r"`?([\w][\w./\-]*\.(?:py|cmd|bat))`?")
missing = {}
for rf in ref_files:
    txt = rf.read_text(encoding="utf-8", errors="replace")
    for mo in pat.finditer(txt):
        ref = mo.group(1).replace("\\", "/").lstrip("/")
        if ref.startswith(("scripts/", "module/", ".claude/")):
            if not (ROOT / ref).exists():
                missing.setdefault(ref, set()).add(rf.name)
if missing:
    for ref, where in sorted(missing.items()):
        rec(False, f"tot: {ref}  (genannt in {', '.join(sorted(where))})", warn_only=True)
else:
    rec(True, "keine toten repo-internen Script-Verweise in Regeln")

section("J. Tote Memory-Referenzen in Regeln/CLAUDE.md")
mempat = re.compile(r"`?((?:feedback|reference|project|user)_[a-z0-9_]+)(?:\.md)?`?")
mem_missing = {}
for rf in ref_files:
    txt = rf.read_text(encoding="utf-8", errors="replace")
    for mo in mempat.finditer(txt):
        slug = mo.group(1)
        raw = mo.group(0)
        if not (raw.endswith(".md") or (raw.startswith("`") and raw.endswith("`")) or ".md" in raw):
            continue
        if MEMDIR.is_dir() and not (MEMDIR / f"{slug}.md").exists():
            mem_missing.setdefault(slug, set()).add(rf.name)
if mem_missing:
    for slug, where in sorted(mem_missing.items()):
        rec(False, f"tote Memory-Referenz: {slug}.md (genannt in {', '.join(sorted(where))})", warn_only=True)
else:
    rec(True, "keine toten Memory-Referenzen in Regeln/CLAUDE.md")


# ---------- Zusammenfassung ----------
n_fail = sum(1 for s, _ in results if s == "FAIL")
n_warn = sum(1 for s, _ in results if s == "WARN")
n_ok = sum(1 for s, _ in results if s == "OK")
print("\n" + "=" * 60)
print(f"AUDIT-ERGEBNIS: {n_ok} OK · {n_warn} WARN · {n_fail} FAIL")
print("=" * 60)
sys.exit(1 if n_fail else 0)
