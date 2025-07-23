from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import logging

from db_pool import execute_query  # eigene Datenbankfunktion

app = FastAPI()

# 🔓 CORS aktivieren (Frontend-Zugriff erlauben)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Im Produktivbetrieb auf deine Domain beschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 Pfad zum Frontend
static_dir = Path(__file__).resolve().parent.parent / "frontend" / "src"
if not static_dir.exists():
    raise RuntimeError(f"❌ Frontend-Verzeichnis nicht gefunden: {static_dir}")

# 🌐 Statische Dateien verfügbar machen (CSS, JS, Icons ...)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 📄 HTML-Seiten ausliefern
@app.get("/")
def serve_index():
    return FileResponse(static_dir / "index.html")

@app.get("/vorhersage")
def serve_vorhersage():
    return FileResponse(static_dir / "vorhersage.html")

@app.get("/historisch")
def serve_historisch():
    return FileResponse(static_dir / "historisch.html")

# 🔮 Wettervorhersagedaten
@app.get("/api/vorhersage")
def get_forecast_data():
    try:
        query = """
            SELECT
                station_id,
                station_name,
                latitude,
                longitude,
                temperatur,
                apparent_temperatur,
                cloud_cover_total,
                precipitation_sum,
                rain,
                sunshine_duration,
                dew_point,
                pressure_msl,
                windspeed_10m,
                abfragezeit,
                date_hour
            FROM dwd_vorhersage
            ORDER BY station_id, abfragezeit;
        """
        return execute_query(query, fetch=True)
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Vorhersage: {e}")
        return JSONResponse(status_code=500, content={"error": "Fehler beim Abrufen der Vorhersage"})

# 🕰 Historische Wetterdaten
@app.get("/api/historische-daten")
def get_historical_data():
    try:
        query = """
            SELECT
                station_id,
                station_name,
                latitude,
                longitude,
                temperatur,
                windspeed_10m,
                sunshine_duration,
                rain,
                precipitation_sum,
                pressure_msl,
                dew_point,
                cloud_cover_total,
                apparent_temperatur,
                date_hour,
                abfragezeit
            FROM dwd_hist_wetterdaten
            ORDER BY station_id, date_hour;
        """
        return execute_query(query, fetch=True)
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der historischen Daten: {e}")
        return JSONResponse(status_code=500, content={"error": "Fehler beim Abrufen der historischen Daten"})
