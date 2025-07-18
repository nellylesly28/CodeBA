from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db_pool import execute_query  # <-- Datenbank-Verbindung

app = FastAPI()

# CORS erlauben, damit Frontend zugreifen darf
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # im Produktivfall besser auf deine Domain beschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🛰 Endpoint für aktuelle Vorhersagedaten (z. B. View: dwd_vorhersage)
@app.get("/api/vorhersage")
def get_forecast_data():
    query = """
        SELECT station_id, station_name, latitude, longitude, timezone, time,
               temperature_2m, windspeed_10m, sunshine_duration,rain,
               precipitation, pressure_msl, dew_point_2m,cloud_cover,apparent_temperature
        FROM dwd_vorhersage
        ORDER BY station_id, time
    """
    result = execute_query(query, fetch=True)
    return result

# 🛰 Endpoint für historische Wetterdaten (z. B. View: dwd_hist_view)
@app.get("/api/historische-daten")
def get_historical_data():
    query = """
        SELECT station_id, station_name, latitude, longitude, timezone, time,rain,
               temperature_2m, windspeed_10m, sunshine_duration,
               precipitation, pressure_msl, dew_point_2m,cloud_cover,apparent_temperature
        FROM dwd_hist_view
        ORDER BY station_id, time
    """
    result = execute_query(query, fetch=True)
    return result
