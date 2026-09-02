# Apple-Kontakte im Hub — Setup & Umzugs-Checkliste

**Typ:** Thema / Technik-Setup
**Zuletzt_gesynct:** 2026-08-16

## Das Wichtigste

Damit Claude „Schreib eine Mail an Falk Gruber" ohne Rückfrage erledigen kann, braucht der Hub Zugriff auf die **Apple-/iCloud-Kontakte**. Das läuft zweigleisig — bewusst, weil beide Wege unterschiedliche Lücken schließen:

| Weg | Was er kann | Wann er funktioniert |
|---|---|---|
| **1. Kontakte-Cache im Hub** (`module/kontakte/kontakte.csv`) | Nachschlagen von Name, Mail, Telefon, Firma | **immer** — auch in Cloud-Sessions, geplanten Läufen, ohne Mac-Freigaben |
| **2. Lokaler Kontakte-MCP** | Live-Lesen **und** Anlegen/Ändern in Apple Kontakte | nur wenn die Claude-Desktop-App auf dem Mac läuft |

Gleiches Muster wie beim [Apple-Kalender-MCP](Apple-Kalender-MCP-Setup.md).

---

## Teil 1 — Kontakte-Cache (Basis, zuerst einrichten)

### 1. Erster Testlauf (Terminal)
```bash
cd ~/Documents/Claude/Projects/business_hub_Dirk_STARTER && \
python3 scripts/kontakte_export.py --dry-run
```
Ausgabe soll etwa lauten: `… 412 Kontakte, davon 380 mit E-Mail`.

**Wenn 0 Kontakte / „nicht nutzbar":** dem Terminal fehlt der Festplattenvollzugriff.
Systemeinstellungen → Datenschutz & Sicherheit → **Festplattenvollzugriff** → Terminal aktivieren → Terminal neu starten. Alternativ läuft es über den langsameren AppleScript-Weg:
```bash
python3 scripts/kontakte_export.py --applescript
```
(einmalig die Rückfragen „Zugriff auf Kontakte" / „Contacts steuern" mit **Erlauben** beantworten)

### 2. Echten Export schreiben
```bash
python3 scripts/kontakte_export.py
python3 scripts/kontakt.py "Falk Gruber"
```

### 3. Täglich automatisch (launchd)
```bash
cp scripts/com.xmedia.hub.kontakte.plist ~/Library/LaunchAgents/ && \
launchctl unload ~/Library/LaunchAgents/com.xmedia.hub.kontakte.plist 2>/dev/null; \
launchctl load ~/Library/LaunchAgents/com.xmedia.hub.kontakte.plist && \
echo "Job aktiv — läuft täglich 06:45"
```
Sofort testen: `launchctl start com.xmedia.hub.kontakte` → danach `logs/kontakte_export.log` prüfen.

> Läuft der Job nicht (leeres Log): `/usr/bin/python3` braucht ebenfalls **Festplattenvollzugriff** (Systemeinstellungen → Datenschutz & Sicherheit → Festplattenvollzugriff → „+" → ⌘⇧G → `/usr/bin/python3`).

### 4. Datenschutz
`module/kontakte/` ist **gitignored** — die Kontaktdaten landen nicht im GitHub-Repo und werden nicht nach außen gesendet. Der Export liest ausschließlich lokal.

---

## Teil 2 — Lokaler Kontakte-MCP (Live-Zugriff + Schreiben)

### 1. Server installieren (Terminal)
```bash
cd ~ && \
git clone https://github.com/jcontini/macos-contacts-mcp.git && \
cd ~/macos-contacts-mcp && \
npm install && npm run build
```
(Falls `npm` fehlt: Node.js von nodejs.org installieren, dann Block erneut.)

### 2. In Claude-Config eintragen (Terminal)
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
data["mcpServers"]["macos-contacts"] = {
    "command": "node",
    "args": [os.path.expanduser("~/macos-contacts-mcp/build/index.js")]
}
with open(cfg, "w") as f: json.dump(data, f, indent=2)
print("OK – Config gespeichert")
PY
```

### 3. Claude neu starten & freigeben
- Claude **komplett beenden** (⌘Q), neu öffnen.
- Rückfragen mit **Erlauben** beantworten: „Zugriff auf Kontakte" + „Contacts steuern" (Automation).
- Prüfen: Systemeinstellungen → Datenschutz & Sicherheit → **Kontakte** → „Claude" aktiv.

### 4. Testen
- „Such Falk Gruber in meinen Kontakten" → Treffer mit Mail/Telefon.
- Danach `python3 scripts/kontakte_export.py` laufen lassen, damit der Cache den gleichen Stand hat.

---

## Bekannte Eigenheiten / Stolpersteine

| Punkt | Verhalten | Umgang |
|---|---|---|
| **iMessage-MCP `search_contacts`** | Schon installiert, läuft aber in Timeout (60 s) — vermutlich fehlende Kontakte-/Automation-Freigabe | Entweder Freigabe nachziehen oder ignorieren; Cache + Kontakte-MCP decken alles ab |
| **Cloud-Session** | Kann auf dem Mac **keine** macOS-Befehle ausführen (`device_bash` = Linux-VM ohne `~/Library`) | Export/Installation immer nativ im Terminal, Cache macht die Daten dann überall verfügbar |
| **Cache-Alter** | Stand max. 24 h | `python3 scripts/kontakt.py --stand` zeigt das Alter; bei frisch angelegten Kontakten Export manuell starten |
| **Doppelte Einträge** | iCloud + lokal liefern denselben Kontakt | Export dedupliziert über Name + erste Mail + Firma |
| **Config-Änderung** | Wirkt erst nach Neustart | Claude ⌘Q + neu öffnen |

## Verlauf
| Datum | Wer | Was |
|---|---|---|
| 2026-08-16 | Claude/Dirk | Cache-Export + Lookup-Script + launchd-Job gebaut, MCP-Weg dokumentiert |
