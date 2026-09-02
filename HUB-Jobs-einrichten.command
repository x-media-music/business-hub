#!/bin/bash
# ------------------------------------------------------------------
# HUB-Jobs einrichten  (Doppelklick genügt)
# Richtet die täglichen Hintergrund-Jobs des Business-Hubs ein:
#   06:45  Kontakte-Export (Apple-Adressbuch -> module/kontakte/kontakte.csv)
#   06:50  Ansicht-Dokumente-Cleanup (Staging -> _archiv, alte Archivkopien weg)
# Läuft rein lokal, sendet nichts, löscht nur verlustsicher.
# ------------------------------------------------------------------
set -u
HUB="/Users/dirkwoehrle/Documents/Claude/Projects/business_hub_Dirk_STARTER"
LA="$HOME/Library/LaunchAgents"
cd "$HUB" || { echo "Hub-Ordner nicht gefunden: $HUB"; exit 1; }
mkdir -p "$LA"

echo "==================================================="
echo " HUB-Jobs einrichten"
echo "==================================================="
echo

for JOB in com.xmedia.hub.kontakte com.xmedia.hub.ansichtcleanup; do
  echo "-> $JOB"
  cp "$HUB/scripts/$JOB.plist" "$LA/" || { echo "   FEHLER beim Kopieren"; continue; }
  launchctl unload "$LA/$JOB.plist" 2>/dev/null
  if launchctl load "$LA/$JOB.plist" 2>/dev/null; then
    echo "   installiert und aktiv"
  else
    echo "   FEHLER beim Laden"
  fi
done

echo
echo "---------------------------------------------------"
echo " Testlauf Ansicht-Cleanup"
echo "---------------------------------------------------"
OUT="$(/usr/bin/python3 "$HUB/scripts/ansicht_dokumente_cleanup.py" 2>&1)"
echo "$OUT" | tail -n 8

if echo "$OUT" | grep -q "Operation not permitted"; then
  echo
  echo "!!! MACOS BLOCKIERT DEN ZUGRIFF !!!"
  echo "Der Job kann erst laufen, wenn /usr/bin/python3 Festplattenvollzugriff hat:"
  echo "  Systemeinstellungen -> Datenschutz & Sicherheit -> Festplattenvollzugriff"
  echo "  -> '+' -> Cmd+Shift+G -> /usr/bin/python3 eintragen -> hinzufuegen -> Schalter AN"
  echo "Danach diese Datei einfach nochmal doppelklicken."
else
  echo
  echo "Alles in Ordnung. Ab morgen laeuft das Cleanup automatisch um 06:50."
fi

echo
echo "Aktive Hub-Jobs:"
launchctl list | grep -i "com.xmedia.hub" || echo "  (keine gefunden)"
echo
echo "Fertig. Fenster kann geschlossen werden."
