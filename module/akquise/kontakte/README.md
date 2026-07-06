# Akquise-Engine — Tannenbaum-Prinzip

Hier lebt die Lead-Recherche. Die **Datenstruktur** ist schon da (leere Listen mit
Kopfzeile), die **Ablauf-Regeln** stehen in `.claude/rules/02_akquise.md`, die
**Steuerung in einfachen Worten** in `ANLEITUNG.md` (Hub-Root).

## Die Daten-Dateien (schon angelegt, noch leer)

| Datei | Rolle |
|---|---|
| `sammelliste.csv` | **Sammelkorb** — frisch recherchierte Leads dieser Runde. Wird nach dem Versand geleert. |
| `bestandsliste.csv` | Alle bereits kontaktierten Leads (wächst dauerhaft). |
| `bestandsliste_telefon.csv` | Nur-Telefon-Leads, geparkt (kein Mail-/Formularweg). |
| `akquise_counter.csv` | Statistik: was wann an wen raus ging. |
| `email_progress.json` | Versand-Fortschritt (welche Mails schon raus). |
| `fehlerspeicher.json` | Bounces/Fehler, die nachbearbeitet werden müssen. |
| `nachbearbeitung.json` | Offene Nachbearbeitungen (neue Adresse suchen etc.). |

## Die Engine-Bausteine (Funktionen)

Diese Scripts **baut dir dein Hub bei Bedarf selbst** — genau dann, wenn du den
jeweiligen Schritt zum ersten Mal brauchst. Du musst nichts vorinstallieren; sag
einfach was du willst (siehe `ANLEITUNG.md`), der Hub legt das passende Script an
und pflegt es weiter. Sollstand der Funktionen:

| Baustein | Aufgabe |
|---|---|
| `run.py` | Steuert einen Tannenbaum-Lauf (Sammlung → Veredelung → Report). |
| `impressum_check.py` | **Veredelung:** ruft die Website eines Leads auf, zieht aus dem Impressum Name/Email/Telefon/Entscheider. |
| `bestand_abgleich.py` | 4-fach-Duplikat-Check gegen die Bestandslisten, entfernt Dubletten aus dem Sammelkorb. |
| `formular_bot.py` | Trägt **Kontaktformulare** automatisch aus, wo keine Mail-Adresse vorhanden ist (browsergesteuert). |
| `email_sender.py` | Versendet die freigegebene Runde (immer erst nach OWNER-GATE). |
| `check_inbox.py` | Prüft Antworten, kategorisiert (Zusage/Absage/unzustellbar). |
| `bounce.py` | **Bounce-Handling:** erkennt unzustellbare Mails, notiert sie im Fehlerspeicher, stößt Neu-Recherche an. |

> **Prinzip:** keine Daten vorgeladen — nur die Struktur und die Regeln. Die
> Intelligenz sitzt im Hub (Claude), der die Bausteine nach `02_akquise.md`
> orchestriert. Nichts geht nach außen ohne dein explizites **OWNER-GATE**.
