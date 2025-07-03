# Wetterstation & Forecast Projekt

Dieses Projekt besteht aus einem Backend (Python) und einem Frontend (HTML), um Wetterdaten zu verarbeiten und darzustellen.

## Projektstruktur

```
CodeBA/root/
├── backend/
│   ├── db_pool.py
│   ├── forecast.py
│   ├── main.py
│   └── wetterstation.py
├── frontend/
│   ├── images/
│   │   └── lesly.jpeg
│   └── src/
│       └── index.html
```

## Backend: Übersicht der Module

| Datei              | Zweck / Funktion                                                                 |
|--------------------|---------------------------------------------------------------------------------|
| **db_pool.py**     | Stellt einen MySQL Connection Pool bereit und bietet die Funktion `execute_query` zur einfachen und effizienten Ausführung von SQL-Queries. |
| **wetterstation.py** | Holt Wetterstationsdaten (historisch als Text, aktuell als HTML) vom DWD, verarbeitet sie und speichert sie in der Datenbank. Enthält Funktionen zum Abrufen, Parsen und Speichern der Stationsdaten. |
| **forecast.py**    | Holt Wettervorhersagedaten (aktuell und historisch) von der Open-Meteo-API für die gespeicherten Stationen, verarbeitet die Daten und speichert sie in der Datenbank. |
| **main.py**        | Einstiegspunkt: Steuert den Ablauf. Aktualisiert die Wetterstationen und ruft die Vorhersagefunktionen auf. Erwartet als Argument 'historisch' oder 'aktuell'. |

### Kurzbeschreibung der Backend-Dateien

- **db_pool.py**: 
  - Erstellt einen MySQL Connection Pool für effiziente Datenbankzugriffe.
  - Bietet die Funktion `execute_query` für SQL-Operationen (Abfragen, Einfügen, Aktualisieren).

- **wetterstation.py**: 
  - Holt historische Wetterstationsdaten als Textdatei und aktuelle als HTML vom Deutschen Wetterdienst (DWD).
  - Parst und speichert die Stationsdaten in die Datenbanktabellen `wetterstation_hist` und `wetterstation_akt`.
  - Funktioniert als Datenbasis für die Vorhersage.

- **forecast.py**: 
  - Holt für alle gespeicherten Stationen Wettervorhersagedaten (aktuell/historisch) von der Open-Meteo-API.
  - Baut die API-URLs dynamisch, verarbeitet die Antworten und speichert die Wetterdaten in der Datenbank.

- **main.py**: 
  - Startet den Gesamtprozess.
  - Erwartet als Argument 'historisch' oder 'aktuell' und ruft entsprechend die Update- und Forecast-Funktionen auf.

## Backend starten

1. Python 3.x installieren
2. Abhängigkeiten installieren (ggf. mit `pip install -r requirements.txt`)
3. Im Verzeichnis `backend/` den Server starten:
   ```bash
   python main.py historisch
   # oder
   python main.py aktuell
   ```

## Frontend

Das Frontend besteht aus einer einfachen HTML-Seite und Bildern. Die Datei `index.html` befindet sich unter `frontend/src/`.

### Nutzung

Öffne die Datei `frontend/src/index.html` im Browser, um die Benutzeroberfläche anzuzeigen.

## Autor

Lesly

## Lizenz

Dieses Projekt steht unter einer freien Lizenz (bitte ggf. anpassen). 