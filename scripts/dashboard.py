#!/usr/bin/env python3
"""
dashboard.py — erzeugt reports/dashboard.html aus den Buchhaltungs-CSVs.

Liest:
  module/buchhaltung/offene_posten.csv
  module/buchhaltung/verarbeitet.csv
  module/buchhaltung/datev_routing.csv
  backups/inbox_state.json   (Inbox-Cursor)

Aufruf:  python3 scripts/dashboard.py
Öffnen:  reports/dashboard.html im Browser.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
BH = HUB / "module" / "buchhaltung"
OUT = HUB / "reports" / "dashboard.html"


def read_csv(path: Path) -> tuple[list[str], list[list[str]]]:
    if not path.exists():
        return [], []
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh, delimiter=";"))
    if not rows:
        return [], []
    return rows[0], rows[1:]


def eur_sum(rows: list[list[str]], idx: int) -> float:
    total = 0.0
    for r in rows:
        if len(r) > idx:
            v = r[idx].replace("€", "").replace(".", "").replace(",", ".").strip()
            try:
                total += float(v)
            except ValueError:
                pass
    return total


def table(headers: list[str], rows: list[list[str]], empty: str) -> str:
    if not rows:
        return f'<p class="empty">{empty}</p>'
    th = "".join(f"<th>{h}</th>" for h in headers)
    trs = ""
    for r in rows:
        tds = "".join(f"<td>{(r[i] if i < len(r) else '')}</td>" for i in range(len(headers)))
        trs += f"<tr>{tds}</tr>"
    return f"<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>"


def main() -> int:
    oh, orows = read_csv(BH / "offene_posten.csv")
    vh, vrows = read_csv(BH / "verarbeitet.csv")
    rh, rrows = read_csv(BH / "datev_routing.csv")

    cursor = "—"
    state_file = HUB / "backups" / "inbox_state.json"
    if state_file.exists():
        try:
            st = json.loads(state_file.read_text(encoding="utf-8"))
            parts = [f"{k}: UID {v.get('last_uid','—')} ({v.get('last_check','')[:16]})" for k, v in st.items()]
            cursor = " · ".join(parts) if parts else "—"
        except json.JSONDecodeError:
            pass

    offen_sum = eur_sum(orows, 2)
    offen_de = f"{offen_sum:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Buchhaltung Dashboard — x-media music GmbH</title>
<style>
  :root {{ --bg:#0f172a; --card:#fff; --ink:#1e293b; --muted:#64748b;
           --accent:#2563eb; --red:#dc2626; --green:#16a34a; --line:#e2e8f0; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:-apple-system,Segoe UI,Roboto,sans-serif;
          background:#f1f5f9; color:var(--ink); }}
  header {{ background:var(--bg); color:#fff; padding:22px 28px; }}
  header h1 {{ margin:0; font-size:19px; }}
  header .sub {{ color:#94a3b8; font-size:13px; margin-top:4px; }}
  .wrap {{ max-width:1000px; margin:0 auto; padding:24px 28px 60px; }}
  .kpis {{ display:flex; gap:16px; flex-wrap:wrap; margin-bottom:8px; }}
  .kpi {{ background:var(--card); border:1px solid var(--line); border-radius:12px;
          padding:16px 20px; flex:1; min-width:170px; }}
  .kpi .n {{ font-size:26px; font-weight:700; }}
  .kpi .l {{ color:var(--muted); font-size:13px; margin-top:2px; }}
  .kpi.red .n {{ color:var(--red); }} .kpi.green .n {{ color:var(--green); }}
  section {{ background:var(--card); border:1px solid var(--line); border-radius:12px;
             padding:18px 20px; margin-top:20px; }}
  section h2 {{ margin:0 0 12px; font-size:15px; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th,td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); }}
  th {{ color:var(--muted); font-weight:600; font-size:12px; text-transform:uppercase; letter-spacing:.03em; }}
  tbody tr:hover {{ background:#f8fafc; }}
  .empty {{ color:var(--green); font-weight:600; }}
  .foot {{ color:var(--muted); font-size:12px; margin-top:24px; text-align:center; }}
</style></head><body>
<header>
  <h1>🧾 Buchhaltung Dashboard — x-media music GmbH</h1>
  <div class="sub">Stand: {now} · Inbox-Cursor: {cursor}</div>
</header>
<div class="wrap">
  <div class="kpis">
    <div class="kpi red"><div class="n">{len(orows)}</div><div class="l">Offene Posten</div></div>
    <div class="kpi red"><div class="n">{offen_de} €</div><div class="l">Offener Betrag</div></div>
    <div class="kpi green"><div class="n">{len(vrows)}</div><div class="l">Belege verarbeitet</div></div>
    <div class="kpi"><div class="n">{len(rrows)}</div><div class="l">Gelernte Zuordnungen</div></div>
  </div>

  <section><h2>🔴 Offene Posten (zu bezahlen)</h2>
    {table(oh, orows, "Keine offenen Posten — alles bezahlt. ✅")}
  </section>

  <section><h2>✅ Verarbeitete Belege</h2>
    {table(vh, vrows, "Noch keine Belege verarbeitet.")}
  </section>

  <section><h2>🧠 Gelernte Zuordnungen (Absender → DATEV-Box)</h2>
    {table(rh, rrows, "Noch keine Zuordnungen gelernt.")}
  </section>

  <div class="foot">Automatisch erzeugt aus den Hub-CSVs · <code>scripts/dashboard.py</code></div>
</div></body></html>"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"✅ Dashboard erzeugt: {OUT}")
    print(f"   Offene Posten: {len(orows)} ({offen_sum:.2f} €) · verarbeitet: {len(vrows)} · Zuordnungen: {len(rrows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
