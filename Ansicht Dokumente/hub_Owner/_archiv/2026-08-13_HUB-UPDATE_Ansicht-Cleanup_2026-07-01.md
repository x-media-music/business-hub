# 🔧 Hub-Update: selbstpflegendes, verlustsicheres Ansicht-Cleanup (2026-07-01)

**Für wen:** Jeden Business-Hub, der aus dem Starter-Mantel entstanden ist.
**Was es bringt:** Dein Staging-Ordner (`Ansicht Dokumente/hub_Owner/`) räumt sich
künftig **von selbst** auf — ohne dass je etwas verloren geht. Der Aufräum-Aufwand
sinkt über die Zeit gegen null.

---

## So wendest du es an (2 Schritte)

1. Diese Datei in deinen **Hub-Ordner** legen (oder in `Downloads` — Hauptsache dein Hub kann sie lesen).
2. Deinem Hub sagen:
   > **„In meinem Hub-Ordner (bzw. in Downloads) liegt die Datei
   > `HUB-UPDATE_Ansicht-Cleanup_2026-07-01.md` — wende dieses Update an."**

Dein Hub macht den Rest. Er richtet nichts nach außen ein und löscht nichts ohne
dein OK — alle heiklen Schritte laufen wie gewohnt über dein OWNER-GATE.

---

## 📋 ANWEISUNG AN DEN HUB (Claude, an dich)

Wende die folgenden Schritte in **diesem** Hub an. Passe alle Pfade an die
tatsächliche Struktur dieses Hubs an (nutze die Hub-Wurzel = der Ordner, in dem
`CLAUDE.md` liegt). Nichts von einem fremden Hub übernehmen.

### Schritt 1 — Cleanup-Script anlegen
Lege die Datei `scripts/ansicht_dokumente_cleanup.py` mit **genau** dem Inhalt aus
dem Codeblock unten an (Abschnitt „SCRIPT"). Das Script ist bereits generisch: es
leitet die Hub-Wurzel aus seinem eigenen Ort ab (`scripts/` → parent.parent).

**Danach anpassen:** Im Script gibt es die Liste `PRODUCTIVE_ROOTS` (wo deine
produktiven Original-Dokumente liegen). Standard sind `module/`, `wissensbasis/`,
`vorlagen/`. **Ergänze** dort alle weiteren Ordner, in denen der Owner echte
Dokumente ablegt (z. B. ein Verträge- oder Projekt-Ordner). Frag den Owner kurz,
wo seine fertigen Dokumente liegen, und trag die Pfade ein. Das ist wichtig, damit
das Sicherheits-Gate „gibt es ein produktives Original?" richtig greift.

### Schritt 2 — Staging-Struktur sicherstellen
Stelle sicher, dass es `Ansicht Dokumente/hub_Owner/_archiv/` in der Hub-Wurzel
gibt (falls nicht: anlegen). Dort liegen Entwürfe zur Ansicht; nach Freigabe +
Versand wandert die Kopie ins `_archiv` (dafür gibt es im Script `archive_now()`).

### Schritt 3 — Regel in `00_core.md` ergänzen
Trag in `.claude/rules/00_core.md` (Abschnitt Ansicht/Staging) ein:
- Das Cleanup läuft **verlustsicher**: archiviert/löscht nur Dateien mit
  produktivem Original; **Einzelkopien** werden gemeldet in
  `reports/ansicht_cleanup_report.md`, nicht angetastet.
- **Beim Session-Start** kurz `reports/ansicht_cleanup_report.md` prüfen; wenn dort
  Einzelkopien gelistet sind, produktiv ablegen.

### Schritt 4 — Automatisch laufen lassen (optional, mit OWNER-GATE)
Damit sich der Ordner ohne Zutun sauber hält, richte einen **täglichen Job** ein,
der `python scripts/ansicht_dokumente_cleanup.py` ausführt. **Passe das an das
Betriebssystem des Owners an** und **frag vorher per OWNER-GATE**, ob du den Job
anlegen darfst:
- **Windows:** Scheduled Task, z. B.
  `schtasks /create /tn "Hub_AnsichtCleanup" /tr "<python> <hubwurzel>\scripts\ansicht_dokumente_cleanup.py" /sc DAILY /st 07:00 /f`
  (python-Pfad des Owners einsetzen; ggf. `.cmd`-Wrapper mit `set PYTHONIOENCODING=utf-8`).
- **macOS:** `launchd`-Agent (plist in `~/Library/LaunchAgents`).
- **Linux:** `cron`-Eintrag (`crontab -e`).
Wenn der Owner keinen Automatik-Job will: einfach das Script beim Session-Start
manuell aufrufen — funktioniert genauso.

### Schritt 5 — Testen
Lauf einmal `python scripts/ansicht_dokumente_cleanup.py --dry-run` und zeig dem
Owner die Zusammenfassung. Dann echt einmal ausführen. Danach diese Update-Datei
ins `_archiv` verschieben (erledigt).

### Schritt 6 — Zurückmelden
Berichte dem Owner in 3–4 Zeilen: was angelegt/geändert wurde, ob der Job läuft,
und wo der Report liegt.

---

## SCRIPT — `scripts/ansicht_dokumente_cleanup.py`

```python
#!/usr/bin/env python3
"""
Ansicht-Dokumente Cleanup (selbstpflegend + verlustsicher)

Raeumt den Staging-Ordner (Ansicht Dokumente/hub_Owner) auf:
1. Staging-Dateien > 7 Tage  -> ins _archiv  (nur wenn produktives Original existiert)
2. Archiv-Dateien   > 30 Tage -> geloescht    (nur wenn produktives Original existiert)
3. Junk (Thumbs.db, leere Ordner) wird entfernt.

Sicherheits-Gate: gibt es KEIN produktives Original (gleicher Dateiname) im Hub,
wird die Datei NICHT angetastet, sondern in reports/ansicht_cleanup_report.md
als "muss produktiv abgelegt werden" gemeldet. So geht nie eine Einzelkopie verloren.

Aufruf:
    python scripts/ansicht_dokumente_cleanup.py
    python scripts/ansicht_dokumente_cleanup.py --dry-run
"""

import sys, os, re, shutil, argparse
from pathlib import Path
from datetime import datetime

# Hub-Wurzel = Ordner ueber scripts/
HUB_ROOT = Path(__file__).resolve().parent.parent
BASE = HUB_ROOT / "Ansicht Dokumente"
HUBS = ["hub_Owner"]
DESKTOP_STAGING = Path.home() / "Desktop" / "Ansicht Dokumente"   # optional
STAGING_MAX_AGE_DAYS = 7
ARCHIV_MAX_AGE_DAYS = 30

# WO produktive Original-Dokumente liegen (Sicherheits-Gate). Hier eigene
# Dokument-Ordner ergaenzen (z.B. einen Vertraege-/Projekte-Ordner)!
PRODUCTIVE_ROOTS = [
    HUB_ROOT / "module",
    HUB_ROOT / "wissensbasis",
    HUB_ROOT / "vorlagen",
    # HUB_ROOT / "<dein_dokumente_ordner>",
]

# Grosse Medien-/Roh-Ordner beim Index-Aufbau ueberspringen (Performance).
SKIP_DIR_PATTERNS = re.compile(
    r"bilder|fotos|photo|rohbilder|studiobilder|pressebilder|demos|videos|"
    r"lightroom|\.git|__pycache__|node_modules|_archiv|thumbs",
    re.IGNORECASE,
)
JUNK_FILES = {"thumbs.db", "desktop.ini", ".ds_store"}
DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}_")
REPORT_PATH = HUB_ROOT / "reports" / "ansicht_cleanup_report.md"


def strip_date_prefix(name): return DATE_PREFIX.sub("", name)


def build_productive_index():
    names = set()
    for root in PRODUCTIVE_ROOTS:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(str(root)):
            dirnames[:] = [d for d in dirnames if not SKIP_DIR_PATTERNS.search(d)]
            for fn in filenames:
                names.add(fn.lower())
    return names


def staging_dirs():
    return [BASE / h for h in HUBS] + [DESKTOP_STAGING]


def age_days(path):
    return (datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)).total_seconds() / 86400


def cleanup(dry_run=False):
    stats = {"moved_to_archive": 0, "deleted_from_archive": 0, "junk_removed": 0,
             "needs_filing": [], "kept_in_archive": [], "errors": []}
    productive = build_productive_index()
    for hub_dir in staging_dirs():
        label = hub_dir.name
        archiv_dir = hub_dir / "_archiv"
        if not hub_dir.exists():
            continue
        archiv_dir.mkdir(parents=True, exist_ok=True)

        # Junk + leere Ordner
        for f in hub_dir.iterdir():
            if f.name == "_archiv":
                continue
            if f.is_file() and f.name.lower() in JUNK_FILES:
                if not dry_run:
                    try: f.unlink()
                    except OSError as e: stats["errors"].append(f"Junk {f}: {e}"); continue
                print(f"[{label}] {'(dry-run) ' if dry_run else ''}junk: {f.name}")
                stats["junk_removed"] += 1
            elif f.is_dir() and not f.name.startswith("."):
                try:
                    contents = [c for c in f.rglob("*") if c.is_file() and c.name.lower() not in JUNK_FILES]
                except OSError:
                    contents = ["?"]
                if not contents:
                    if not dry_run:
                        try: shutil.rmtree(f)
                        except OSError as e: stats["errors"].append(f"Ordner {f}: {e}"); continue
                    print(f"[{label}] {'(dry-run) ' if dry_run else ''}leerer Ordner: {f.name}/")
                    stats["junk_removed"] += 1

        # Staging -> Archiv (nur mit produktivem Original)
        for f in hub_dir.iterdir():
            if not f.is_file() or f.name.startswith(".") or f.name.lower() in JUNK_FILES:
                continue
            try: age = age_days(f)
            except OSError as e: stats["errors"].append(f"{f}: {e}"); continue
            if age <= STAGING_MAX_AGE_DAYS:
                continue
            if f.name.lower() not in productive:
                stats["needs_filing"].append(f"{label}: {f.name}")
                print(f"[{label}] SKIP (keine produktive Kopie -> ablegen!): {f.name} ({age:.1f}d)")
                continue
            target = archiv_dir / f"{datetime.now().strftime('%Y-%m-%d')}_{f.name}"
            if not dry_run:
                try: shutil.move(str(f), str(target))
                except (OSError, shutil.Error) as e: stats["errors"].append(f"Move {f}: {e}"); continue
            print(f"[{label}] {'(dry-run) ' if dry_run else ''}archive: {f.name} ({age:.1f}d)")
            stats["moved_to_archive"] += 1

        # Archiv-Loeschung (nur mit produktivem Original)
        for f in archiv_dir.iterdir():
            if not f.is_file() or f.name.startswith("."):
                continue
            if f.name.lower() in JUNK_FILES:
                if not dry_run:
                    try: f.unlink()
                    except OSError: pass
                stats["junk_removed"] += 1
                continue
            try: age = age_days(f)
            except OSError as e: stats["errors"].append(f"{f}: {e}"); continue
            if age <= ARCHIV_MAX_AGE_DAYS:
                continue
            if strip_date_prefix(f.name).lower() not in productive:
                stats["kept_in_archive"].append(f"{label}: {f.name}")
                print(f"[{label}] KEEP (keine produktive Kopie -> nicht loeschen): {f.name} ({age:.1f}d)")
                continue
            if not dry_run:
                try: f.unlink()
                except OSError as e: stats["errors"].append(f"Delete {f}: {e}"); continue
            print(f"[{label}] {'(dry-run) ' if dry_run else ''}delete: {f.name} ({age:.1f}d)")
            stats["deleted_from_archive"] += 1
    return stats


def archive_now(file_path, hub="hub_Owner"):
    """Verschiebt eine Datei sofort ins Archiv (z.B. nach Freigabe + Versand)."""
    archiv_dir = BASE / hub / "_archiv"
    archiv_dir.mkdir(parents=True, exist_ok=True)
    target = archiv_dir / f"{datetime.now().strftime('%Y-%m-%d')}_{file_path.name}"
    shutil.move(str(file_path), str(target))
    return target


def write_report(stats):
    lines = ["# Ansicht-Cleanup — Report",
             f"**Lauf:** {datetime.now().strftime('%d.%m.%Y %H:%M')}", "",
             f"- Archiviert: {stats['moved_to_archive']}",
             f"- Geloescht (Archiv >30T): {stats['deleted_from_archive']}",
             f"- Junk entfernt: {stats['junk_removed']}", ""]
    if stats["needs_filing"]:
        lines += ["## ⚠️ Muss produktiv abgelegt werden (Einzelkopien im Staging)"]
        lines += [f"- {x}" for x in stats["needs_filing"]] + [""]
    if stats["kept_in_archive"]:
        lines += ["## 🛟 Im Archiv behalten (keine produktive Kopie)"]
        lines += [f"- {x}" for x in stats["kept_in_archive"]] + [""]
    if not stats["needs_filing"] and not stats["kept_in_archive"]:
        lines += ["✅ Alles sauber — kein Handlungsbedarf."]
    try:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not BASE.exists():
        print(f"Staging-Basis {BASE} existiert nicht - nichts zu tun."); return 0
    stats = cleanup(dry_run=args.dry_run)
    if not args.dry_run:
        write_report(stats)
    print("\nZusammenfassung:")
    print(f"  Archiviert:           {stats['moved_to_archive']}")
    print(f"  Aus Archiv geloescht: {stats['deleted_from_archive']}")
    print(f"  Junk entfernt:        {stats['junk_removed']}")
    if stats["needs_filing"]:
        print(f"  ⚠️  Einzelkopien (bitte produktiv ablegen): {len(stats['needs_filing'])}")
        for x in stats["needs_filing"]: print(f"      - {x}")
    if stats["errors"]:
        print(f"  Fehler: {len(stats['errors'])}")
        for e in stats["errors"]: print(f"    - {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

*Update erstellt 01.07.2026. Bei Fragen: einfach deinen Hub fragen — oder bei Tammo melden.*
