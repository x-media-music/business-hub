"""
Wissensbasis-Index Generator
Liest alle .md-Dateien aus wissensbasis/ und erzeugt INDEX.md als durchsuchbare Übersicht.
Aufruf: python scripts/wissensbasis_index.py
"""

import os
import re
from datetime import datetime

# Hub-Wurzel unabhängig vom Laufwerk: Script liegt in scripts/, parent.parent = Hub-Wurzel.
WISSENSBASIS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "wissensbasis")
INDEX_FILE = os.path.join(WISSENSBASIS_DIR, "INDEX.md")


def parse_entry(filepath):
    """Extrahiert Metadaten aus einer Wissensbasis-.md-Datei."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    entry = {
        "datei": os.path.basename(filepath),
        "pfad": filepath.replace("\\", "/"),
        "ordner": os.path.basename(os.path.dirname(filepath)),
        "name": "",
        "typ": "",
        "status": "",
        "email": "",
        "ort": "",
        "firma": "",
    }

    for line in lines[:20]:
        line = line.strip()

        # Titel aus H1
        if line.startswith("# ") and not entry["name"]:
            entry["name"] = line[2:].strip()

        # Metadaten-Felder
        match = re.match(r"\*\*(\w[\w\-]*?):\*\*\s*(.*)", line)
        if match:
            key = match.group(1).lower().replace("-", "_")
            val = match.group(2).strip()
            if key == "typ":
                entry["typ"] = val
            elif key == "status":
                entry["status"] = val
            elif key == "email":
                entry["email"] = val
            elif key == "ort":
                entry["ort"] = val
            elif key == "firma":
                entry["firma"] = val

    return entry


def generate_index():
    """Generiert INDEX.md aus allen Wissensbasis-Einträgen."""
    entries = []

    for folder in sorted(os.listdir(WISSENSBASIS_DIR)):
        folder_path = os.path.join(WISSENSBASIS_DIR, folder)
        if not os.path.isdir(folder_path) or folder.startswith("."):
            continue
        for filename in sorted(os.listdir(folder_path)):
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(folder_path, filename)
            try:
                entry = parse_entry(filepath)
                entries.append(entry)
            except Exception as e:
                print(f"  FEHLER bei {filepath}: {e}")

    # Index-Datei schreiben
    lines = []
    lines.append(f"# Wissensbasis-Index")
    lines.append(f"**Generiert:** {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    lines.append(f"**Einträge:** {len(entries)}")
    lines.append(f"")
    lines.append(f"> Automatisch generiert von `scripts/wissensbasis_index.py` — nicht manuell bearbeiten!")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # Haupttabelle
    lines.append(f"## Alle Einträge")
    lines.append(f"")
    lines.append(f"| Name | Typ | Status | Datei |")
    lines.append(f"|------|-----|--------|-------|")

    for e in entries:
        name = e["name"][:60] if e["name"] else e["datei"]
        typ = e["typ"] or "—"
        status = e["status"] or "—"
        datei = f"`{e['ordner']}/{e['datei']}`"
        lines.append(f"| {name} | {typ} | {status} | {datei} |")

    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    # Nach Typ gruppiert
    typen = {}
    for e in entries:
        typ = e["typ"] or "Unbekannt"
        if "Veranstalter" in typ or "Lead" in typ:
            group = "Veranstalter / Leads"
        elif "Künstler" in typ or "Band" in typ:
            group = "Künstler / Bands"
        elif "Projekt" in typ:
            group = "Projekte"
        elif "Absage" in typ:
            group = "Absagen"
        elif "Dienstleister" in typ or "Extern" in typ:
            group = "Dienstleister / Extern"
        else:
            group = "Sonstige"

        typen.setdefault(group, []).append(e)

    lines.append(f"## Nach Kategorie")
    lines.append(f"")

    for group in ["Veranstalter / Leads", "Künstler / Bands", "Projekte", "Dienstleister / Extern", "Absagen", "Sonstige"]:
        if group not in typen:
            continue
        lines.append(f"### {group} ({len(typen[group])})")
        for e in typen[group]:
            name = e["name"][:60] if e["name"] else e["datei"]
            extra = ""
            if e["email"]:
                extra += f" | {e['email']}"
            if e["ort"]:
                extra += f" | {e['ort']}"
            lines.append(f"- **{name}**{extra}")
        lines.append(f"")

    # Schnellsuche-Hinweis
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"## Suche")
    lines.append(f"```bash")
    lines.append(f'grep -ri "Suchbegriff" wissensbasis/')
    lines.append(f"```")

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"INDEX.md generiert: {len(entries)} Einträge")
    return entries


if __name__ == "__main__":
    generate_index()
