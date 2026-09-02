# Prompt für die technische Session (x-media Gehirn) — Buchhaltungs-App

**Erstellt:** 29.08.2026 · **Anlass:** Rechnung Jonas Schoof RE620280721 kam nicht bei DATEV an
**Einzugeben in:** technische Session (Buchhaltungs-App / Supabase / n8n)

---

## Prompt zum Kopieren

> Es geht um die Buchhaltungs-App (buchhaltung.xmedia24.com, React-PWA + Supabase,
> Tabelle `bh_belege`). Seit 11.08.2026 gilt: **der Hub führt**, die App ist nur Anzeige-
> und Freigabe-Tool; `scripts/bh_send.py` im Hub liefert aus (music → DATEV-Uploadmail,
> event → Dropbox). Bitte zwei Dinge lösen — einen Bug und ein fehlendes Feature.
>
> ### Problem 1 (Bug): Freigabe mit Box-Wechsel geht verloren
>
> Ändere ich beim Freigeben in der App zusätzlich die Box oder die Firma, schreibt die App
> `dirk_entscheidung='box_geaendert'` bzw. `'firma_geaendert'` statt `'freigegeben'` und
> setzt gleichzeitig `status='verarbeitet'`. Folge: Der Beleg ist weder „freigegeben" (der
> Hub-Versand übersah ihn) noch „wartend" (taucht in keiner offenen Liste auf) — er
> **verschwindet lautlos**. Betroffen waren 5 Belege, u. a. Jonas Schoof RE620280721 über
> 1.943,84 €, die ich in DATEV vergeblich gesucht habe.
>
> Zweiter Fehler derselben Stelle: Beim Box-Wechsel wird `datev_kategorie` aktualisiert,
> aber `datev_email` **nicht mitgezogen**. Im Fall Schoof stand die Kategorie auf `bank`,
> die Adresse aber noch auf Rechnungseingang (`5cc1bdc1-…`). Der Hub nimmt `datev_email`
> vorrangig vor der Box → der Beleg wäre in der falschen DATEV-Box gelandet.
>
> **Bitte in der App:**
> - Eine Freigabe ist eine Freigabe: `dirk_entscheidung='freigegeben'` setzen, auch wenn
>   Box oder Firma geändert wurden. Die Korrektur gehört in eigene Felder
>   (`datev_kategorie` / `firma` / `dropbox_ordner`) bzw. ins Protokoll — nicht in den
>   Entscheidungswert. Falls `box_geaendert`/`firma_geaendert` fachlich gebraucht wird,
>   dann als zusätzliches Kennzeichen, nicht anstelle der Freigabe.
> - `status` erst auf `verarbeitet` setzen, wenn `verarbeitet_am` gefüllt ist. Vorher
>   bleibt der Beleg sichtbar. Ein Beleg darf nie gleichzeitig „fertig" aussehen und
>   unausgeliefert sein.
> - `datev_email` beim Box-Wechsel mitziehen — **besser:** in der App gar nicht setzen und
>   die Adresse immer im Hub aus der Box ableiten (dort steht die gepflegte Box→Adress-
>   Tabelle, Stand 03.08.2026). Eine Quelle der Wahrheit statt zwei.
>
> *Hinweis: Die Hub-Seite ist bereits gefixt* — `bh_send.py` akzeptiert seit 29.08.2026
> alle drei Entscheidungswerte als Freigabe (`FREIGABE_WERTE`, Stichtag
> `BOXCHANGE_GOLIVE`). Das ist bewusst nur ein Auffangnetz; die saubere Lösung gehört in
> die App. Bitte den Hub-Fix nicht rückbauen, er soll als Sicherung bleiben.
>
> ### Problem 2 (Feature): „ist schon bezahlt" als Ein-Klick-Vermerk
>
> Der eigentliche Anlass ist ein **wiederkehrender Vorgang, aber keine feste Regel**:
> Immer wieder muss eine Eingangsrechnung sofort bezahlt werden — per Sofortüberweisung
> über das BW-Bank-Portal oder per PayPal. Das läuft am DATEV-Zahlungsverkehr vorbei.
>
> **Wichtig zum Verständnis, sonst wird das falsch gebaut:**
> - Der Hub schlägt korrekt **Rechnungseingang** vor. Dieser Vorschlag ist richtig und
>   soll so bleiben — er ist der Normalfall.
> - Wenn ich von Rechnungseingang auf **Bank** umstelle, ist das **keine Routing-Korrektur**,
>   sondern eine **Zahlungsinformation**: „diese Rechnung habe ich an DATEV vorbei bereits
>   selbst bezahlt". Deshalb ist sie kein offener Posten mehr und gehört in die Bank-Box
>   (bzw. bei event nach `XE bezahlte Eingangsrechnungen`).
> - Das hängt **nicht am Absender**. Derselbe Musiker kann beim einen Mal normal über
>   Rechnungseingang laufen und beim nächsten Mal sofort bezahlt werden. Es ist eine
>   Entscheidung **pro einzelner Rechnung**, spontan, nach Kassenlage und Dringlichkeit.
>
> **Bitte in der App:**
> - Ein **Ein-Klick-Vermerk beim Freigeben**: „schon bezahlt → Bank" (music) bzw.
>   „schon bezahlt → bezahlte ER" (event). Ein Tap statt Box aufklappen, Wert suchen,
>   umstellen, freigeben. Das ist der eigentliche Zeitgewinn.
> - Optional daneben die selteneren Fälle: bezahlt per Mastercard → Kreditkarte Master,
>   bar → Kasse. Wichtig: **PayPal zählt zu Bank**, nicht zu Mastercard.
> - Den Vermerk in `bh_belege` festhalten (z. B. Feld `zahlweg` = `offen` | `bezahlt_bank` |
>   `bezahlt_master` | `bar`), damit Hub und Protokoll nachvollziehen können, **warum** die
>   Box abweicht. Der freie Kommentar soll erhalten bleiben.
>
> **Ausdrücklich NICHT bauen — Anti-Requirement:**
> Kein Lernen und keine Vorbelegung dieses Vermerks pro Rechnungssteller. „Sofort bezahlt"
> ist eine Ad-hoc-Entscheidung; eine gelernte Vorbelegung würde mich systematisch in die
> falsche Box führen und wäre schlimmer als der heutige Zustand. Der Standardvorschlag
> bleibt **immer** der aus dem Hub-Routing (in der Regel Rechnungseingang); der Vermerk
> gilt genau für diesen einen Beleg. Die bestehende lernende Absender-Zuordnung
> (`datev_routing.csv`, z. B. Lastschrift-Absender wie UTA oder Brevo) bleibt davon
> unberührt — die betrifft feste Zahlwege, nicht diesen Fall.
>
> ### Akzeptanzkriterien
>
> 1. Ich gebe einen Beleg mit geänderter Box frei → er wird ausgeliefert und ist in DATEV
>    bzw. Dropbox auffindbar, in der **richtigen** Box.
> 2. Kein Beleg kann `status='verarbeitet'` haben, solange `verarbeitet_am` leer ist.
> 3. „Schon bezahlt" ist mit einem Tap erledigt, ohne Box-Auswahl.
> 4. Beim nächsten Beleg desselben Absenders steht der Vorschlag wieder auf
>    Rechnungseingang — der Vermerk wirkt **nicht** nach.
> 5. Im Beleg ist später erkennbar, dass die Bank-Box auf „schon bezahlt" beruht.
>
> Bitte zeig mir zuerst deinen Umsetzungsvorschlag inkl. nötiger Schema-Änderungen an
> `bh_belege`, bevor du etwas deployst — der Hub arbeitet parallel auf derselben Tabelle.

---

## Hub-Seite

- `datev_routing.csv` **bleibt unverändert.** Jonas Schoof steht dort korrekt auf
  „Überweisung (offen) → Rechnungseingang" — das ist der Normalfall. Die Sofortzahlung ist
  eine Ausnahme pro Rechnung und darf nicht in die Routing-Tabelle wandern (Dirk 29.08.2026:
  „Es ist nicht immer so … das ist keine obligatorische Sache").
- Nachziehen, sobald die App ein Feld `zahlweg` liefert: `bh_send.py` kann die Zielbox dann
  daraus ableiten, statt sich auf `datev_kategorie`/`datev_email` zu verlassen.
