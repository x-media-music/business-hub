#!/bin/bash
# ------------------------------------------------------------------
# Zugangsdaten in den Passwortmanager übertragen  (Doppelklick genügt)
#
# Führt Feld für Feld durch alle 8 Zugangsdaten des Hubs.
# JEDES Feld landet einzeln in der Zwischenablage — du fügst nur ein
# (Cmd+V) und drückst Enter. Nie abtippen, nie selbst kopieren.
# Das Skript liest nur; es ändert nichts und sendet nichts.
# ------------------------------------------------------------------
set -u
HUB="$(cd "$(dirname "$0")" && pwd)"
S="$HUB/scripts"

lies() {  # $1=Datei  $2=Variable
  python3 -c "
import sys
key, datei = sys.argv[1], sys.argv[2]
for zeile in open(datei):
    zeile = zeile.strip()
    if zeile.startswith(key + '='):
        print(zeile.split('=', 1)[1].strip().strip('\"').strip(\"'\"))
        break
" "$2" "$1"
}

warte() {  # $1=Wert (für erneutes Kopieren)
  local e
  while true; do
    read -r -p "     [Enter] eingefügt, weiter    [w] nochmal kopieren : " e
    case "$e" in
      w|W) printf '%s' "$1" | pbcopy; echo "     -> liegt wieder in der Zwischenablage." ;;
      *)   break ;;
    esac
  done
}

feld() {  # $1=Feldname  $2=Wert  $3=sichtbar(ja/nein)
  printf '%s' "$2" | pbcopy
  echo
  echo "   ------------------------------------------------"
  echo "   In der App in das Feld  >>> $1 <<<  klicken"
  echo "   ------------------------------------------------"
  if [ "$3" = "ja" ]; then
    echo "   Das kommt hinein:  $2"
  else
    echo "   Das kommt hinein:  (${#2} Zeichen, hier nicht angezeigt)"
    echo "   ACHTUNG: im Passwort-Feld steht ein Vorschlag der App."
    echo "            Erst Cmd+A (alles markieren), dann Cmd+V."
  fi
  echo "   Es liegt bereits in der Zwischenablage -> Cmd+V"
  warte "$2"
}

NR=0
GESAMT=8
START=1

eintrag() {  # $1=Titel $2=Benutzername $3=Website $4=Datei $5=Variable
  NR=$((NR + 1))
  [ "$NR" -lt "$START" ] && return 0
  local wert
  wert="$(lies "$4" "$5")"
  if [ -z "$wert" ]; then
    echo "  !! $5 fehlt in $(basename "$4") — übersprungen"
    return 0
  fi
  echo
  echo "==================================================="
  echo " EINTRAG $NR von $GESAMT   —   $1"
  echo "==================================================="
  echo " In der Passwörter-App jetzt auf  +  klicken"
  echo " und \"Neues Passwort\" wählen."
  read -r -p " Enter, wenn das leere Formular offen ist " _
  feld "Titel"        "$1"    ja
  feld "Benutzername" "$2"    ja
  feld "Website"      "$3"    ja
  feld "Passwort"     "$wert" nein
  echo
  echo "   Das Feld \"Notizen\" bleibt LEER."
  echo
  read -r -p "   Eintrag sichern, dann Enter für den nächsten " _
}

clear
echo "==================================================="
echo " Zugangsdaten in den Passwortmanager übertragen"
echo "==================================================="
echo
echo " So läuft es:"
echo "   - Passwörter-App offen lassen, dieses Fenster daneben"
echo "   - jedes Feld liegt einzeln in der Zwischenablage"
echo "   - du fügst nur ein (Cmd+V) und drückst Enter"
echo
echo " Es gibt genau 4 Felder: Titel, Benutzername, Website, Passwort."
echo " Das Feld \"Notizen\" bleibt immer leer."
echo
echo " WICHTIG: nichts selbst kopieren — sonst ist der Wert weg."
echo " Passiert das doch: einfach [w] drücken, dann liegt er wieder da."
echo
read -r -p " Bei welchem Eintrag starten? (1-8, Enter = 1) " ANTWORT
case "$ANTWORT" in
  [1-8]) START="$ANTWORT" ;;
  *)     START=1 ;;
esac
echo " Starte bei Eintrag $START."

# --- Postfächer (Strato) ---
eintrag "Strato Webmail – info@xmedia24.com"        "info@xmedia24.com"        "strato.de" "$S/mail.env" "MAIL_INFO_PASSWORD"
eintrag "Strato Webmail – rechnung@xmedia24.com"    "rechnung@xmedia24.com"    "strato.de" "$S/mail.env" "MAIL_RECHNUNG_PASSWORD"
eintrag "Strato Webmail – anfrage@xmedia24.com"     "anfrage@xmedia24.com"     "strato.de" "$S/mail.env" "MAIL_ANFRAGE_PASSWORD"
eintrag "Strato Webmail – ninox@xmedia24.com"       "ninox@xmedia24.com"       "strato.de" "$S/mail.env" "MAIL_NINOX_PASSWORD"
eintrag "Strato Webmail – info@xmedia-event.de"     "info@xmedia-event.de"     "strato.de" "$S/mail.env" "MAIL_INFO_EVENT_PASSWORD"
eintrag "Strato Webmail – rechnung@xmedia-event.de" "rechnung@xmedia-event.de" "strato.de" "$S/mail.env" "MAIL_RECHNUNG_EVENT_PASSWORD"

# --- Supabase Service-Role-Keys ---
eintrag "Supabase Hub – CRM (Service-Role-Key)"         "vrntqlmrxlbnhetskwjw" "supabase.com" "$S/crm_keys.env"         "SUPABASE_SERVICE_ROLE_KEY"
eintrag "Supabase Hub – Buchhaltung (Service-Role-Key)" "hsvpjtpzsnfdpibdkxut" "supabase.com" "$S/buchhaltung_keys.env" "SUPABASE_SERVICE_ROLE_KEY"

printf 'fertig' | pbcopy
echo
echo "==================================================="
echo " Fertig. Zwischenablage wurde geleert."
echo "==================================================="
echo
echo " Kontrolle in der Passwörter-App:"
echo "   6 Einträge  strato.de"
echo "   2 Einträge  supabase.com"
echo
read -r -p " Enter zum Schließen " _
