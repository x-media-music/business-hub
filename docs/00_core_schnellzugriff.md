## 🔎 SCHNELLZUGRIFF AUFS WISSEN (recall)

Bei JEDER „Stand / was ist mit X / gibt es schon Y / was war wann"-Frage → ZUERST:
```
python scripts/recall/recall.py "<frage oder stichworte>"     (Kurz: recall "<frage>")
```
Sucht in einem Aufruf über alle Speicher, gerankt nach Relevanz + Aktualität, mit
Quelle + Pfad + Snippet. Danach das Original öffnen — recall ersetzt das Quell-Lesen nicht.
Beim Beenden zusätzlich: `journal.py` (Historie sichern) + `memory_index.py` (Index frisch).
