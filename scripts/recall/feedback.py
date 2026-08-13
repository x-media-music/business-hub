#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
feedback.py — Feedback- & Zusammenhang-Erfassung pro Aufgabe.

Idee: der Owner gibt NACH jeder Aufgabe Feedback (Lob / Korrektur / Hinweis auf einen
Aufgaben-Zusammenhang). Es wird SOFORT hier notiert. Nach einigen Aufgaben wird
ausgewertet → wiederkehrende Muster werden zu Regeln/Memories/Scripts.

  python scripts/recall/feedback.py add "…" [--type korrektur|lob|dep|regel] [--task "kontext"] [--read "mein read"]
  python scripts/recall/feedback.py review        # Auswertung: Typen + wiederkehrende Themen
  python scripts/recall/feedback.py list [--n 20]  # letzte Einträge

Log liegt in logs/feedback_log.md (append-only) und ist über recall.py durchsuchbar.
type=dep = ein Wenn-Dann/Aktion-Reaktion-Zusammenhang → fließt ins Gesamtbild
(logs/prozess_graph.md wird bei review daraus verdichtet).
"""
import os, re, sys, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _hubpaths import hub_root

HUB = hub_root()
LOG = os.path.join(HUB, "logs", "feedback_log.md")
GRAPH = os.path.join(HUB, "logs", "prozess_graph.md")

TYPES = {"korrektur": "🔴 Korrektur", "lob": "🟢 Lob",
         "dep": "🔗 Zusammenhang", "regel": "📏 Regel-Kandidat"}

STOP = set("""der die das und oder ein eine ist sind war ich du er sie es wir nicht
nur wie was wer wo bei mit auf aus für von den dem des als auch am um so muss
soll dann wenn immer mal noch schon sehr man werden wird haben hat dass dabei
kontext mein read kandidat korrektur zusammenhang aufgabe aufgaben""".split())

def _read(p):
    try:
        with open(p, encoding="utf-8", errors="ignore") as f: return f.read()
    except Exception: return ""

def add(args):
    typ = args.type if args.type in TYPES else "korrektur"
    ts = time.strftime("%Y-%m-%d %H:%M")
    block = [f"\n## {ts} · {TYPES[typ]}"]
    if args.task: block.append(f"**Kontext:** {args.task}")
    block.append(f"> {args.text.strip()}")
    if args.read: block.append(f"→ Mein Read: {args.read.strip()}")
    block.append("")
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    if not os.path.isfile(LOG):
        with open(LOG, "w", encoding="utf-8") as f:
            f.write("# 📝 Feedback-Log — pro Aufgabe (auswerten via `feedback.py review`)\n"
                    "> Feedback wird hier sofort festgehalten, "
                    "regelmäßig ausgewertet → Muster werden zu Regeln/Memories.\n")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write("\n".join(block) + "\n")
    print(f"notiert [{TYPES[typ]}] {ts}")

def _entries():
    txt = _read(LOG)
    out = []
    for blk in re.split(r"\n## ", txt):
        if "·" not in blk: continue
        head, *rest = blk.splitlines()
        body = " ".join(rest)
        typ = next((t for t in TYPES.values() if t in head), "?")
        out.append((head.strip(), typ, body))
    return out

def review(args):
    ents = _entries()
    if not ents:
        print("Noch kein Feedback erfasst."); return
    print(f"\n📊 FEEDBACK-AUSWERTUNG — {len(ents)} Einträge\n" + "="*60)
    # nach Typ
    from collections import Counter
    tc = Counter(t for _, t, _ in ents)
    for t, n in tc.most_common():
        print(f"  {t}: {n}")
    # wiederkehrende Themen (Keyword-Häufung über alle Einträge)
    words = Counter()
    for _, _, body in ents:
        for w in re.findall(r"[a-zA-ZäöüÄÖÜß]{4,}", body.lower()):
            if w not in STOP: words[w] += 1
    recurring = [(w, n) for w, n in words.most_common(15) if n >= 2]
    print("\n🔁 Wiederkehrende Themen (≥2×) — Kandidaten für eine Regel:")
    if recurring:
        for w, n in recurring: print(f"  {n}×  {w}")
    else:
        print("  (noch keine Häufung — mehr Feedback sammeln)")
    deps = [e for e in ents if e[1] == TYPES["dep"]]
    print(f"\n🔗 Erfasste Zusammenhänge (Wenn-Dann): {len(deps)}"
          + ("  → in logs/prozess_graph.md verdichten" if deps else ""))
    for head, _, body in deps[-8:]:
        print(f"  · {body[:120]}")
    print("="*60)
    print("Nächster Schritt: gehäufte Themen in eine Memory/Regel gießen, "
          "erledigte Feedback-Punkte im Log als [erledigt] markieren.")

def lst(args):
    ents = _entries()
    for head, typ, body in ents[-(args.n):]:
        print(f"{head}\n   {body[:160]}\n")

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("add"); a.add_argument("text")
    a.add_argument("--type", default="korrektur"); a.add_argument("--task", default="")
    a.add_argument("--read", default="")
    sub.add_parser("review")
    l = sub.add_parser("list"); l.add_argument("--n", type=int, default=20)
    args = ap.parse_args()
    if args.cmd == "add": add(args)
    elif args.cmd == "review": review(args)
    elif args.cmd == "list": lst(args)
    else: ap.print_help()

if __name__ == "__main__":
    main()
