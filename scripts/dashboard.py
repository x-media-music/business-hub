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

Interaktiv (rein im Browser, kein Server nötig):
  • Offene Posten: Häkchen "✓ Frei" auswählen → Button "📋 Freigabe kopieren"
    kopiert einen Befehl in die Zwischenablage, den Dirk Claude in den Chat
    einfügt. Claude leitet dann an DATEV weiter / legt in Dropbox ab.
  • Häkchen "Erledigt": streicht die Zeile durch / blendet sie aus. Der Stand
    wird pro Rechnung im Browser gemerkt (localStorage) und übersteht das
    Neu-Erzeugen des Dashboards.
"""
from __future__ import annotations

import csv
import html as _html
import json
import re
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
    header = rows[0]
    data = [r for r in rows[1:] if any((c or "").strip() for c in r)]
    return header, data


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
    th = "".join(f"<th>{_html.escape(h)}</th>" for h in headers)
    trs = ""
    for r in rows:
        tds = "".join(
            f"<td>{_html.escape(r[i]) if i < len(r) else ''}</td>"
            for i in range(len(headers))
        )
        trs += f"<tr>{tds}</tr>"
    return f"<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>"


def _forwarded_date(steller: str, rg: str, notiz: str,
                    processed: list[tuple[str, str]]) -> str | None:
    """Übergabe-Datum, wenn der Beleg schon an DATEV/Dropbox übergeben wurde
    (kanonisch aus verarbeitet.csv, ersatzweise aus dem Notiz-Feld) — sonst None."""
    rgl = rg.lower().strip()
    st = steller.lower()
    tokens = re.findall(r"[a-zäöüß0-9]{4,}", st)
    stoken = tokens[0] if tokens else ""
    # 1) verarbeitet.csv (Beschreibung enthält Steller + RgNr)
    if rgl:
        for desc, date in processed:
            if rgl in desc and (not stoken or stoken in desc):
                return date
    # 2) Fallback: Notiz nach "übergeben/abgelegt <Datum>" durchsuchen
    m = re.search(r"(?:übergeben|abgelegt)\s+(\d{2}\.\d{2}\.\d{4})", notiz, re.IGNORECASE)
    if m:
        return m.group(1)
    if re.search(r"in dropbox|liegt in dropbox", notiz, re.IGNORECASE):
        return "abgelegt"
    return None


def offene_table(headers: list[str], rows: list[list[str]], empty: str,
                 vrows: list[list[str]]) -> str:
    """Interaktive Tabelle der offenen Posten mit Freigabe- + Erledigt-Häkchen.
    Bereits übergebene Belege werden markiert und für die Freigabe gesperrt."""
    if not rows:
        return f'<p class="empty">{empty}</p>'
    processed = [(r[1].lower(), r[0]) for r in vrows if len(r) >= 2]
    th = (
        '<th class="col-cb">✓ Frei</th>'
        '<th class="col-cb">Erledigt</th>'
        '<th class="col-fw">📤 Übergeben</th>'
        + "".join(f"<th>{_html.escape(h)}</th>" for h in headers)
    )
    trs = ""
    for r in rows:
        steller = r[0] if len(r) > 0 else ""
        rg = r[1] if len(r) > 1 else ""
        betrag = r[2] if len(r) > 2 else ""
        box = r[4] if len(r) > 4 else ""
        # Notiz kann selbst Semikolons enthalten → alle Restspalten zusammenfassen
        notiz = ";".join(r[6:]) if len(r) > 6 else ""
        key = f"{steller}||{rg}"
        ka = _html.escape(key, quote=True)
        sa = _html.escape(steller, quote=True)
        ra = _html.escape(rg, quote=True)
        ba = _html.escape(box, quote=True)
        bta = _html.escape(betrag, quote=True)
        fw = _forwarded_date(steller, rg, notiz, processed)
        row_cls = ' class="forwarded"' if fw else ""
        if fw:
            fw_disp = "📤 " + fw
            fw_cell = (
                f'<td class="col-fw"><span class="fw-badge" '
                f'title="bereits an DATEV/Dropbox übergeben">{_html.escape(fw_disp)}</span></td>'
            )
            cb = (
                '<td class="col-cb"><input type="checkbox" class="frei-cb" disabled '
                'title="schon übergeben – keine erneute Freigabe nötig"></td>'
            )
        else:
            fw_cell = '<td class="col-fw"></td>'
            cb = (
                f'<td class="col-cb"><input type="checkbox" class="frei-cb" '
                f'data-key="{ka}" data-steller="{sa}" data-rg="{ra}" '
                f'data-box="{ba}" data-betrag="{bta}"></td>'
            )
        er = (
            f'<td class="col-cb"><input type="checkbox" class="erl-cb" '
            f'data-key="{ka}" data-steller="{sa}" data-rg="{ra}" '
            f'data-box="{ba}" data-betrag="{bta}"></td>'
        )
        tds = "".join(
            f"<td>{_html.escape(r[i]) if i < len(r) else ''}</td>"
            for i in range(len(headers))
        )
        trs += f'<tr data-key="{ka}"{row_cls}>{cb}{er}{fw_cell}{tds}</tr>'
    return (
        f'<table id="offene-table"><thead><tr>{th}</tr></thead>'
        f"<tbody>{trs}</tbody></table>"
    )


# --- Interaktivität (kein f-string → keine Klammer-Verdopplung nötig) ---------
SCRIPT = r"""
<script>
(function(){
  var STORE='bh_erledigt', HIDE='bh_hidedone';
  function load(){ try{ return JSON.parse(localStorage.getItem(STORE)||'{}'); }catch(e){ return {}; } }
  function save(o){ localStorage.setItem(STORE, JSON.stringify(o)); }
  var done = load();
  var rows = Array.prototype.slice.call(document.querySelectorAll('#offene-table tbody tr'));

  function applyRow(tr){
    var k = tr.getAttribute('data-key');
    var erl = !!done[k];
    tr.classList.toggle('done', erl);
    var cb = tr.querySelector('.erl-cb'); if(cb) cb.checked = erl;
  }
  function applyHide(){
    var hide = localStorage.getItem(HIDE)==='1';
    var t = document.getElementById('toggle-hidedone'); if(t) t.checked = hide;
    rows.forEach(function(tr){
      tr.style.display = (hide && tr.classList.contains('done')) ? 'none' : '';
    });
    var n = rows.filter(function(tr){ return tr.classList.contains('done'); }).length;
    var badge = document.getElementById('done-count');
    if(badge) badge.textContent = n ? (n + ' erledigt') : '';
  }

  rows.forEach(applyRow);
  applyHide();

  document.querySelectorAll('.erl-cb').forEach(function(cb){
    cb.addEventListener('change', function(){
      var k = cb.getAttribute('data-key');
      if(cb.checked){ done[k] = true; } else { delete done[k]; }
      save(done);
      applyRow(cb.closest('tr'));
      applyHide();
      updateBasket();
    });
  });

  function updateBasket(){
    var sel = document.querySelectorAll('.frei-cb:checked');
    var selErl = document.querySelectorAll('.erl-cb:checked');
    var b = document.getElementById('basket');
    document.getElementById('basket-count').textContent = sel.length + ' Posten zur Freigabe';
    var ec = document.getElementById('erl-count');
    if(ec) ec.textContent = selErl.length + ' bezahlt/erledigt';
    b.classList.toggle('show', (sel.length + selErl.length) > 0);
    document.getElementById('copy-msg').textContent = '';
  }
  document.querySelectorAll('.frei-cb').forEach(function(cb){
    cb.addEventListener('change', updateBasket);
  });

  function copyText(text, done){
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(text).then(function(){ done(true); }, function(){ fallback(); });
    } else { fallback(); }
    function fallback(){
      var ta=document.createElement('textarea'); ta.value=text;
      ta.style.position='fixed'; ta.style.opacity='0'; document.body.appendChild(ta); ta.select();
      var ok=false; try{ ok=document.execCommand('copy'); }catch(e){}
      document.body.removeChild(ta); done(ok);
    }
  }
  var copyBtn = document.getElementById('copy-btn');
  if(copyBtn){
    copyBtn.addEventListener('click', function(){
      var sel = document.querySelectorAll('.frei-cb:checked');
      if(!sel.length) return;
      var lines = ['Freigabe Buchhaltung — bitte diese Posten weiterleiten/ablegen und danach als erledigt vermerken:'];
      sel.forEach(function(cb){
        lines.push('- ' + cb.getAttribute('data-steller') + ' | Rg ' + cb.getAttribute('data-rg')
                   + ' | ' + cb.getAttribute('data-betrag') + ' | ' + cb.getAttribute('data-box'));
      });
      copyText(lines.join('\n'), function(ok){
        document.getElementById('copy-msg').textContent = ok
          ? '✓ kopiert – jetzt Claude in den Chat einfügen'
          : 'Kopieren nicht möglich – bitte Text manuell übernehmen';
      });
    });
  }

  var copyErlBtn = document.getElementById('copy-erl-btn');
  if(copyErlBtn){
    copyErlBtn.addEventListener('click', function(){
      var sel = document.querySelectorAll('.erl-cb:checked');
      if(!sel.length) return;
      var lines = ['Bezahlt/erledigt Buchhaltung — bitte diese Posten als erledigt aus den offenen Posten streichen:'];
      sel.forEach(function(cb){
        lines.push('- ' + cb.getAttribute('data-steller') + ' | Rg ' + cb.getAttribute('data-rg')
                   + ' | ' + cb.getAttribute('data-betrag') + ' | ' + cb.getAttribute('data-box'));
      });
      copyText(lines.join('\n'), function(ok){
        document.getElementById('copy-msg').textContent = ok
          ? '✓ kopiert – jetzt Claude in den Chat einfügen'
          : 'Kopieren nicht möglich – bitte Text manuell übernehmen';
      });
    });
  }

  var t = document.getElementById('toggle-hidedone');
  if(t){ t.addEventListener('change', function(){ localStorage.setItem(HIDE, t.checked?'1':'0'); applyHide(); }); }
  updateBasket();
})();
</script>
"""

BASKET = """
<div id="basket" class="basket">
  <span id="basket-count">0 Posten zur Freigabe</span>
  <button id="copy-btn">📋 Freigabe kopieren</button>
  <span class="basket-sep">·</span>
  <span id="erl-count">0 bezahlt/erledigt</span>
  <button id="copy-erl-btn">📋 Bezahlt/erledigt kopieren</button>
  <span id="copy-msg"></span>
</div>
"""


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
  .wrap {{ max-width:1000px; margin:0 auto; padding:24px 28px 100px; }}
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
  th,td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top; }}
  th {{ color:var(--muted); font-weight:600; font-size:12px; text-transform:uppercase; letter-spacing:.03em; }}
  tbody tr:hover {{ background:#f8fafc; }}
  .empty {{ color:var(--green); font-weight:600; }}
  .col-cb {{ width:52px; text-align:center; white-space:nowrap; }}
  .col-cb input {{ width:17px; height:17px; cursor:pointer; }}
  tr.done td {{ text-decoration:line-through; color:#94a3b8; }}
  tr.done {{ opacity:.6; }}
  tr.done .col-cb {{ text-decoration:none; }}
  .col-fw {{ width:104px; white-space:nowrap; }}
  .fw-badge {{ display:inline-block; background:#dcfce7; color:#166534; border-radius:6px;
               padding:2px 7px; font-size:11.5px; font-weight:600; }}
  tr.forwarded .frei-cb {{ opacity:.3; cursor:not-allowed; }}
  .h2ctrl {{ float:right; font-size:12px; font-weight:400; color:var(--muted);
             text-transform:none; letter-spacing:0; display:flex; gap:12px; align-items:center; }}
  .h2ctrl label {{ cursor:pointer; display:flex; gap:5px; align-items:center; }}
  #done-count {{ color:var(--green); }}
  .basket {{ position:fixed; left:0; right:0; bottom:0; background:var(--bg); color:#fff;
             padding:13px 20px; display:flex; align-items:center; gap:18px; justify-content:center;
             transform:translateY(130%); transition:transform .22s ease; z-index:50;
             box-shadow:0 -6px 20px rgba(0,0,0,.18); }}
  .basket.show {{ transform:translateY(0); }}
  .basket button {{ background:var(--accent); color:#fff; border:0; border-radius:8px;
                    padding:10px 18px; font-size:14px; font-weight:600; cursor:pointer; }}
  .basket button:hover {{ background:#1d4ed8; }}
  #basket-count {{ font-size:14px; }}
  #copy-msg {{ color:#4ade80; font-size:13px; min-width:1px; }}
  .hint {{ color:var(--muted); font-size:12px; margin:0 0 10px; }}
  .foot {{ color:var(--muted); font-size:12px; margin-top:24px; text-align:center; }}
  .toast {{ position:fixed; left:50%; bottom:84px; transform:translateX(-50%) translateY(20px);
            background:var(--green); color:#fff; padding:11px 20px; border-radius:10px; font-size:14px;
            font-weight:600; opacity:0; pointer-events:none; transition:all .25s ease; z-index:60;
            box-shadow:0 6px 20px rgba(0,0,0,.25); }}
  .toast.show {{ opacity:1; transform:translateX(-50%) translateY(0); }}
  #live-hint {{ display:none; }}
  .live-badge {{ display:none; background:#16a34a; color:#fff; font-size:12px; font-weight:600;
                 padding:3px 10px; border-radius:20px; margin-left:10px; vertical-align:middle; }}
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

  <section><h2>🔴 Offene Posten (zu bezahlen)
      <span class="h2ctrl">
        <span id="done-count"></span>
        <label><input type="checkbox" id="toggle-hidedone"> erledigte ausblenden</label>
      </span>
    </h2>
    <p class="hint">Zum <b>Weiterleiten an DATEV/Dropbox</b>: „✓ Frei" ankreuzen → unten <b>Freigabe kopieren</b> → mir in den Chat einfügen. — Für <b>schon bezahlt/erledigt</b>: „Erledigt" ankreuzen → unten <b>Bezahlt/erledigt kopieren</b> → mir einfügen, dann streiche ich die Posten endgültig aus der Liste. (Ohne diesen Schritt bleibt „Erledigt" nur eine Notiz im Browser und der Posten kommt wieder.) Belege mit <b>📤 Übergeben</b> sind schon an DATEV/Dropbox raus (nur Zahlung offen).</p>
    {offene_table(oh, orows, "Keine offenen Posten — alles bezahlt. ✅", vrows)}
  </section>

  <section><h2>✅ Verarbeitete Belege</h2>
    {table(vh, vrows, "Noch keine Belege verarbeitet.")}
  </section>

  <section><h2>🧠 Gelernte Zuordnungen (Absender → DATEV-Box)</h2>
    {table(rh, rrows, "Noch keine Zuordnungen gelernt.")}
  </section>

  <div class="foot">Automatisch erzeugt aus den Hub-CSVs · <code>scripts/dashboard.py</code></div>
</div>
{BASKET}
{SCRIPT}
</body></html>"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"✅ Dashboard erzeugt: {OUT}")
    print(f"   Offene Posten: {len(orows)} ({offen_sum:.2f} €) · verarbeitet: {len(vrows)} · Zuordnungen: {len(rrows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
