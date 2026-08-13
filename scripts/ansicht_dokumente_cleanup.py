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
