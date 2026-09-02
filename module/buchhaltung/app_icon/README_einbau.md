# App-Icon Buchhaltung (buchhaltung.xmedia24.com)

Neues, eindeutiges Icon: weißer Beleg mit € und Zackenrand auf blauem Grund (#2563eb).
Klar unterscheidbar von der anderen x-media-App.

## Was hier liegt

| Datei | Zweck |
|---|---|
| `icon_master.svg` | Quelldatei (skalierbar, für spätere Änderungen) |
| `icon-512.png` … `icon-16.png` | Alle benötigten Pixelgrößen |
| `icon-512-maskable.png`, `icon-192-maskable.png` | Android/PWA „maskable" (mit Rand) |
| `favicon.ico` | Browser-Tab / Taskleiste (16/32/48 gebündelt) |
| `manifest_icons_snippet.json` | `icons`-Block für die PWA-`manifest.json` |
| `head_snippet.html` | `<link>`-Zeilen für den `<head>` der App |

## Einbau in die App (Hostinger, React-PWA)

Das Icon liegt jetzt fertig vor — der eigentliche Austausch passiert im Quellcode
der Buchhaltungs-App (separates Projekt, nicht in diesem Hub):

1. **PNG/ICO kopieren** nach `public/icons/` (bzw. `favicon.ico` nach `public/`).
2. **`manifest.json`**: den `icons`-Block aus `manifest_icons_snippet.json`
   übernehmen (Pfade ggf. an den echten Ordner anpassen).
3. **`index.html` `<head>`**: die Zeilen aus `head_snippet.html` einfügen
   (alte `apple-touch-icon`/`icon`-Zeilen vorher entfernen).
4. **Deploy** auf Hostinger (Build + Upload wie gewohnt).

## Auf dem iPhone/Mac sichtbar machen

iOS und die Taskleiste cachen das alte Icon hartnäckig:

- **iPhone:** die App vom Homebildschirm löschen → Safari öffnen →
  buchhaltung.xmedia24.com neu laden → „Teilen" → „Zum Home-Bildschirm".
- **Mac/Taskleiste:** installierte PWA entfernen und neu installieren, oder
  Browser-Cache für die Domain leeren.

Ohne Neu-Hinzufügen zeigt iOS oft noch das alte Symbol.
