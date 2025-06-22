import requests
import json
from datetime import datetime, timedelta
from db_pool import execute_query

# Koordinaten synchron aus DB holen
def get_coordinates(table_name, offset, limit):
    query = f"""
        SELECT latitude, longitude
        FROM {table_name}
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        LIMIT %s OFFSET %s
    """
    return execute_query(query, (limit, offset), fetch=True)

# Forecast-URL aufbauen
def build_url(coords, case):
    if case == "historisch":
        base_url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=14)
        date_params = f"&start_date={start_date}&end_date={end_date}"
    else:
        base_url = "https://api.open-meteo.com/v1/forecast"
        date_params = "&forecast_days=2"

    lat_list = ",".join(str(row['latitude']) for row in coords)
    lon_list = ",".join(str(row['longitude']) for row in coords)

    return (
        f"{base_url}?latitude={lat_list}&longitude={lon_list}"
        f"{date_params}"
        "&hourly=temperature_2m,windspeed_10m,sunshine_duration,"
        "precipitation,pressure_msl,dew_point_2m"
        "&models=icon_seamless"
        "&timezone=Europe/Berlin"
    )

# JSON in DB speichern
def store_response(table_name, json_data):
    insert_query = f"INSERT INTO {table_name} (daten) VALUES (%s)"
    try:
        execute_query(insert_query, (json.dumps(json_data),))
        print("Erfolgreich gespeichert.")
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")

# Hauptfunktion
def run_forecast(case):
    print(f"Starte Forecast für: {case}")

    if case == "historisch":
        station_table = "wetterstation_hist"
        storage_table = "wetterdaten_hist"
    elif case == "aktuell":
        station_table = "wetterstation_akt"
        storage_table = "vorhersage_akt"
    else:
        print("Ungültiger Fall. Nur 'historisch' oder 'aktuell' erlaubt.")
        return

    offset = 0
    limit = 20
    index = 1

    while True:
        coords = get_coordinates(station_table, offset, limit)
        if not coords:
            print("Alle Koordinaten wurden verarbeitet.")
            break

        url = build_url(coords, case)
        print(f"Anfrage {index} (Offset {offset})")

        try:
            response = requests.get(url)
            if response.status_code == 200:
                json_data = response.json()
                store_response(storage_table, json_data)
                print(f"Gruppe {index} gespeichert.")
            else:
                print(f"HTTP Fehler: {response.status_code}")
        except Exception as e:
            print(f"Ausnahme in Gruppe {index}: {e}")

        offset += limit
        index += 1
