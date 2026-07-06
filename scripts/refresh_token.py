"""
refresh_token.py — Template für Microsoft-Token-Verwaltung.

PLATZHALTER-SCRIPT — nach Azure-App-Setup mit Leben füllen. Siehe README.md.

Zweck (wenn produktiv):
- Erstes Login via Browser (Device-Code- oder Auth-Code-Flow)
- Refresh-Token in tokens/microsoft_token.json speichern
- Bei jedem Graph-Call: Access-Token via Refresh-Token neu holen

Nutzung:
    python refresh_token.py --initial-login   # einmalig, öffnet Browser
    python refresh_token.py                   # Access-Token holen (wird von
                                              # send_email.py/check_inbox.py
                                              # intern aufgerufen)
"""
from __future__ import annotations

import argparse
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--initial-login", action="store_true")
    args = ap.parse_args()

    print("⚠️  Dieses Script ist ein TEMPLATE.")
    print("    Azure-App-Setup siehe scripts/README.md.")
    if args.initial_login:
        print("    → Initial-Login würde hier Browser öffnen")
        print("      (MSAL public client auth code flow).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
