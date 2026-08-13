# Apple-Kalender-MCP — Setup & Umzugs-Checkliste (neuer Mac)

**Typ:** Thema / Technik-Setup
**Zuletzt_gesynct:** 2026-07-19

## Das Wichtigste

Gibt Claude **Lese- + Schreibzugriff auf den Apple-/iCloud-Kalender „Dirk"** (Haupt­kalender, ~3356 Termine). Nötig, weil der Google-Connector nur die Google-Kalender sieht, nicht iCloud. Läuft als **lokaler MCP-Server auf dem Mac** (Python, über AppleScript).

- **Eingerichtet:** 19.07.2026 auf „Laptop-von-Dirk"
- **Server-Projekt:** https://github.com/andrewbergsma/apple-calendar-mcp
- **Installationsort:** `~/apple-calendar-mcp/`
- **Claude-Config:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **OWNER-GATE gilt:** Termine anlegen/ändern/löschen nur nach Dirks „Ja".

---

## Umzugs-Checkliste für einen NEUEN Mac

### 1. Server installieren (Terminal)
```bash
cd ~ && \
git clone https://github.com/andrewbergsma/apple-calendar-mcp.git && \
cd ~/apple-calendar-mcp && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt
```
(Falls macOS nach „Command Line Tools" fragt → installieren, dann Block erneut.)

### 2. Deutsche-Locale-Fix anwenden (Terminal)
Der Original-Server formatiert Datumsangaben englisch → AppleScript scheitert auf dem deutschen Mac. Fix:
```bash
python3 - <<'PY'
import os, shutil
p = os.path.expanduser("~/apple-calendar-mcp/apple_calendar_mcp.py")
shutil.copy(p, p + ".backup2")
s = open(p, encoding="utf-8").read()
s = s.replace('strftime("%B %d, %Y at %I:%M:%S %p")', 'strftime("%d.%m.%Y %H:%M:%S")')
s = s.replace('strftime("%B %d, %Y")', 'strftime("%d.%m.%Y")')
open(p, "w", encoding="utf-8").write(s)
print("Geändert: JA")
PY
```

### 3. In Claude-Config eintragen (Terminal)
```bash
python3 - <<'PY'
import json, os, shutil
cfg_dir = os.path.expanduser("~/Library/Application Support/Claude")
cfg = os.path.join(cfg_dir, "claude_desktop_config.json")
os.makedirs(cfg_dir, exist_ok=True)
data = {}
if os.path.exists(cfg):
    shutil.copy(cfg, cfg + ".backup")
    try:
        with open(cfg) as f: data = json.load(f)
    except Exception: data = {}
data.setdefault("mcpServers", {})
data["mcpServers"]["apple-calendar"] = {
    "command": os.path.expanduser("~/apple-calendar-mcp/venv/bin/python3"),
    "args": [os.path.expanduser("~/apple-calendar-mcp/apple_calendar_mcp.py")]
}
with open(cfg, "w") as f: json.dump(data, f, indent=2)
print("OK – Config gespeichert")
PY
```

### 4. Claude neu starten & Kalender freigeben
- Claude **komplett beenden** (⌘Q) und neu öffnen.
- macOS-Abfrage „Claude möchte auf deinen Kalender zugreifen" → **Vollzugriff / Erlauben**.
  (Prüfen unter: Systemeinstellungen → Datenschutz & Sicherheit → Kalender → „Claude" = Vollzugriff.)

### 5. Testen
- Claude: „Zeig meinen Kalender heute/morgen" → sollte Termine listen.
- Claude: Test-Termin anlegen + wieder löschen.

---

## Bekannte Eigenheiten / Stolpersteine

| Punkt | Verhalten | Umgang |
|---|---|---|
| **Deutsche Locale** | Ohne Fix (Schritt 2): „Datum ungültig" beim Anlegen | Fix zwingend anwenden |
| **create-Meldung** | Termin wird korrekt angelegt, aber die Erfolgsmeldung wirft einen Fehler (`date string … Unicode`) | Nach dem Anlegen per „heute/Liste" gegenprüfen — Fehlermeldung ignorieren |
| **list_events Range** | `end_date` = gleicher Tag → 0 Treffer (Range 00:00–00:00) | `end_date` = einen Tag später wählen |
| **Änderungen laden** | Neuer Code/Config wirkt erst nach Neustart | Claude ⌘Q + neu öffnen |

## Verlauf
| Datum | Wer | Was |
|---|---|---|
| 2026-07-19 | Claude/Dirk | Server installiert, Locale-Fix, Config-Eintrag, getestet (lesen+anlegen+löschen OK auf „Dirk") |
