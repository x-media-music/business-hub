#!/bin/bash
# ------------------------------------------------------------------
# Zugangsdaten im Passwortmanager pruefen  (Doppelklick genuegt)
#
# Vergleicht jeden Eintrag der Passwoerter-App mit der echten Datei
# im Hub. Es wird NICHTS angezeigt und NICHTS geaendert — nur
# verglichen und OK / FEHLER gemeldet.
#
# Ablauf je Eintrag: in der Passwoerter-App den Eintrag mit der
# rechten Maustaste anklicken -> "Passwort kopieren", dann hier Enter.
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

NR=0
OK=0
FEHLER=0
LISTE_FEHLER=""
VORHER=""

pruefe() {  # $1=Anzeigename  $2=Datei  $3=Variable
  NR=$((NR + 1))
  local soll ist
  soll="$(lies "$2" "$3")"
  echo
  echo "---------------------------------------------------"
  echo " $NR von 8 :  $1"
  echo "---------------------------------------------------"
  echo " In der Passwoerter-App diesen Eintrag mit der rechten"
  echo " Maustaste anklicken -> \"Passwort kopieren\"."
  read -r -p " Kopiert? Enter zum Pruefen (s = ueberspringen) " EING
  if [ "$EING" = "s" ] || [ "$EING" = "S" ]; then
    echo "   uebersprungen"
    return 0
  fi
  ist="$(pbpaste | tr -d '\r\n')"

  if [ -z "$ist" ]; then
    echo "   FEHLER: Zwischenablage ist leer."
    FEHLER=$((FEHLER + 1)); LISTE_FEHLER="$LISTE_FEHLER\n   - $1 (nichts kopiert)"
  elif [ -n "$VORHER" ] && [ "$ist" = "$VORHER" ]; then
    echo "   FEHLER: Zwischenablage unveraendert seit dem letzten Eintrag."
    echo "           Wurde wirklich kopiert?"
    FEHLER=$((FEHLER + 1)); LISTE_FEHLER="$LISTE_FEHLER\n   - $1 (nicht neu kopiert)"
  elif [ "$ist" = "$soll" ]; then
    echo "   OK  — stimmt exakt mit dem Hub ueberein (${#soll} Zeichen)"
    OK=$((OK + 1))
  else
    echo "   FEHLER: stimmt NICHT."
    echo "           im Passwortmanager: ${#ist} Zeichen"
    echo "           im Hub erwartet:    ${#soll} Zeichen"
    FEHLER=$((FEHLER + 1)); LISTE_FEHLER="$LISTE_FEHLER\n   - $1"
  fi
  VORHER="$ist"
}

clear
echo "==================================================="
echo " Zugangsdaten im Passwortmanager pruefen"
echo "==================================================="
echo
echo " Es wird nur verglichen. Nichts wird angezeigt,"
echo " nichts geaendert, nichts gesendet."
echo
read -r -p " Enter zum Starten " _

pruefe "Strato: info@xmedia24.com"        "$S/mail.env" "MAIL_INFO_PASSWORD"
pruefe "Strato: rechnung@xmedia24.com"    "$S/mail.env" "MAIL_RECHNUNG_PASSWORD"
pruefe "Strato: anfrage@xmedia24.com"     "$S/mail.env" "MAIL_ANFRAGE_PASSWORD"
pruefe "Strato: ninox@xmedia24.com"       "$S/mail.env" "MAIL_NINOX_PASSWORD"
pruefe "Strato: info@xmedia-event.de"     "$S/mail.env" "MAIL_INFO_EVENT_PASSWORD"
pruefe "Strato: rechnung@xmedia-event.de" "$S/mail.env" "MAIL_RECHNUNG_EVENT_PASSWORD"
pruefe "Supabase: Hub CRM"                "$S/crm_keys.env"         "SUPABASE_SERVICE_ROLE_KEY"
pruefe "Supabase: Hub Buchhaltung"        "$S/buchhaltung_keys.env" "SUPABASE_SERVICE_ROLE_KEY"

printf 'fertig' | pbcopy
echo
echo "==================================================="
echo " ERGEBNIS:   $OK korrekt,   $FEHLER fehlerhaft"
echo "==================================================="
if [ "$FEHLER" -gt 0 ]; then
  echo
  echo " Diese Eintraege stimmen nicht:"
  printf "%b\n" "$LISTE_FEHLER"
  echo
  echo " Sag Claude, welche es sind — er legt dir den"
  echo " richtigen Wert einzeln in die Zwischenablage."
else
  echo
  echo " Alles korrekt gesichert. Zwischenablage geleert."
fi
echo
read -r -p " Enter zum Schliessen " _
