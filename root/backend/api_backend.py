from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import logging
from fastapi.responses import StreamingResponse
import time
import json
import asyncio

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

@app.get("/zeitanalyse")
def serve_zeitanalyse():
    return FileResponse(static_dir / "zeitanalyse.html")

# 🔮 Wettervorhersagedaten

#@app.get("/api/vorhersage")

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

#def get_forecast_data():
#    try:
#        query = """
     #       SELECT
     #           station_id,
     #           station_name,
     #           latitude,
     #           longitude,
     #           temperatur,
     #           apparent_temperatur,
     #           cloud_cover_total,
     #           precipitation_sum,
     #           rain,
     #           sunshine_duration,
     #           dew_point,
     #           pressure_msl,
     #           windspeed_10m,
     #           abfragezeit,
     #           date_hour
     #       FROM dwd_vorhersage
     #       ORDER BY station_id, abfragezeit;
#        """
#        return execute_query(query, fetch=True)
#    except Exception as e:
#        logging.error(f"Fehler beim Abrufen der Vorhersage: {e}")
#        return JSONResponse(status_code=500, content={"error": "Fehler beim Abrufen der Vorhersage"})

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





@app.get("/api/zeitanalyse")
def get_time_analysis(metric: str = "temperatur", start_date: str = None, end_date: str = None):
    try:
        metric_lc = (metric or "").lower()
        if metric_lc not in ("temperatur",):
            return JSONResponse(
                status_code=400,
                content={"error": "Nur 'temperatur' wird aktuell unterstützt."}
            )
        
        # Standard-Zeitraum falls keine Daten angegeben
        if not start_date or not end_date:
            from datetime import datetime, timedelta
            now = datetime.now()
            start_date = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
            end_date = (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        
        # SQL für alle Stationen mit Temperaturdaten im gewählten Zeitraum
        sql_station = """
        WITH combined AS (
            SELECT 
                station_id,
                station_name,
                latitude,
                longitude,
                CAST(REPLACE(apparent_temperatur, ',', '.') AS DECIMAL(5,2)) AS temp,
                date_hour
            FROM dwd_hist_wetterdaten
            WHERE apparent_temperatur IS NOT NULL 
                AND apparent_temperatur != ''
                AND date_hour BETWEEN %s AND %s
            
            UNION ALL
            
            SELECT 
                station_id,
                station_name,
                latitude,
                longitude,
                CAST(REPLACE(apparent_temperatur, ',', '.') AS DECIMAL(5,2)) AS temp,
                date_hour
            FROM dwd_vorhersage
            WHERE apparent_temperatur IS NOT NULL 
                AND apparent_temperatur != ''
                AND date_hour BETWEEN %s AND %s
        )
        SELECT 
            station_id,
            station_name,
            latitude,
            longitude,
            date_hour,
            temp,
            MIN(temp) OVER(PARTITION BY station_id, date_hour) AS min_temp,
            MAX(temp) OVER(PARTITION BY station_id, date_hour) AS max_temp
        FROM combined
        ORDER BY station_id, date_hour
        """
        
        # Top 5 kälteste Temperaturen im Zeitraum
        sql_top5_cold = """
        WITH combined AS (
            SELECT 
                station_id,
                station_name,
                latitude,
                longitude,
                CAST(REPLACE(apparent_temperatur, ',', '.') AS DECIMAL(5,2)) AS temp,
                date_hour
            FROM dwd_hist_wetterdaten
            WHERE apparent_temperatur IS NOT NULL 
                AND apparent_temperatur != ''
                AND date_hour BETWEEN %s AND %s
            
            UNION ALL
            
            SELECT 
                station_id,
                station_name,
                latitude,
                longitude,
                CAST(REPLACE(apparent_temperatur, ',', '.') AS DECIMAL(5,2)) AS temp,
                date_hour
            FROM dwd_vorhersage
            WHERE apparent_temperatur IS NOT NULL 
                AND apparent_temperatur != ''
                AND date_hour BETWEEN %s AND %s
        )
        SELECT * FROM combined 
        ORDER BY temp ASC 
        LIMIT 5
        """
        
        # Top 5 wärmste Temperaturen im Zeitraum
        sql_top5_warm = """
        WITH combined AS (
            SELECT 
                station_id,
                station_name,
                latitude,
                longitude,
                CAST(REPLACE(apparent_temperatur, ',', '.') AS DECIMAL(5,2)) AS temp,
                date_hour
            FROM dwd_hist_wetterdaten
            WHERE apparent_temperatur IS NOT NULL 
                AND apparent_temperatur != ''
                AND date_hour BETWEEN %s AND %s
            
            UNION ALL
            
            SELECT 
                station_id,
                station_name,
                latitude,
                longitude,
                CAST(REPLACE(apparent_temperatur, ',', '.') AS DECIMAL(5,2)) AS temp,
                date_hour
            FROM dwd_vorhersage
            WHERE apparent_temperatur IS NOT NULL 
                AND apparent_temperatur != ''
                AND date_hour BETWEEN %s AND %s
        )
        SELECT * FROM combined 
        ORDER BY temp DESC 
        LIMIT 5
        """
        
        # Top 5 kälteste Temperaturen ALLER Zeiten (unabhängig vom Zeitraum)
        sql_top5_cold_alltime = """
        WITH combined AS (
            SELECT 
                station_id,
                station_name,
                latitude,
                longitude,
                CAST(REPLACE(apparent_temperatur, ',', '.') AS DECIMAL(5,2)) AS temp,
                date_hour
            FROM dwd_hist_wetterdaten
            WHERE apparent_temperatur IS NOT NULL 
                AND apparent_temperatur != ''
            
            UNION ALL
            
            SELECT 
                station_id,
                station_name,
                latitude,
                longitude,
                CAST(REPLACE(apparent_temperatur, ',', '.') AS DECIMAL(5,2)) AS temp,
                date_hour
            FROM dwd_vorhersage
            WHERE apparent_temperatur IS NOT NULL 
                AND apparent_temperatur != ''
        )
        SELECT * FROM combined 
        ORDER BY temp ASC 
        LIMIT 5
        """
        
        # Top 5 wärmste Temperaturen ALLER Zeiten (unabhängig vom Zeitraum)
        sql_top5_warm_alltime = """
        WITH combined AS (
            SELECT 
                station_id,
                station_name,
                latitude,
                longitude,
                CAST(REPLACE(apparent_temperatur, ',', '.') AS DECIMAL(5,2)) AS temp,
                date_hour
            FROM dwd_hist_wetterdaten
            WHERE apparent_temperatur IS NOT NULL 
                AND apparent_temperatur != ''
            
            UNION ALL
            
            SELECT 
                station_id,
                station_name,
                latitude,
                longitude,
                CAST(REPLACE(apparent_temperatur, ',', '.') AS DECIMAL(5,2)) AS temp,
                date_hour
            FROM dwd_vorhersage
            WHERE apparent_temperatur IS NOT NULL 
                AND apparent_temperatur != ''
        )
        SELECT * FROM combined 
        ORDER BY temp DESC 
        LIMIT 5
        """
        
        # Daten abrufen mit Zeitraum-Parametern
        rows = execute_query(sql_station, (start_date, end_date, start_date, end_date), fetch=True)
        top5_cold = execute_query(sql_top5_cold, (start_date, end_date, start_date, end_date), fetch=True)
        top5_warm = execute_query(sql_top5_warm, (start_date, end_date, start_date, end_date), fetch=True)
        
        # Top 5 aller Zeiten (unabhängig vom Zeitraum)
        top5_cold_alltime = execute_query(sql_top5_cold_alltime, fetch=True)
        top5_warm_alltime = execute_query(sql_top5_warm_alltime, fetch=True)
        
        return {
            "rows": rows,
            "top5_cold": top5_cold,
            "top5_warm": top5_warm,
            "top5_cold_alltime": top5_cold_alltime,
            "top5_warm_alltime": top5_warm_alltime,
            "time_range": {"start": start_date, "end": end_date}
        }
        
    except Exception as e:
        logging.error(f"Fehler beim Abrufen der Zeitanalyse: {e}")
        return JSONResponse(status_code=500, content={"error": "Fehler beim Abrufen der Zeitanalyse"})
