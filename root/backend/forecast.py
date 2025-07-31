import requests
import json
from datetime import datetime, timedelta
from db_pool import execute_query
from error_handler import log_info, log_error, log_warning, smart_retry

#🔁 Retry-fähiger API-Aufruf
@smart_retry(max_retries=6, base_delay=60)
def get_with_retry(url):
    return requests.get(url)


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
def build_url(coords, case, start_date=None, end_date=None):
    hourly_params = "temperature_2m,rain,cloud_cover,precipitation,apparent_temperature,dew_point_2m,pressure_msl,windspeed_10m,sunshine_duration"

    if case == "historisch":
        base_url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

        if not start_date or not end_date:
            raise ValueError("Start- und Enddatum sind für historisch erforderlich")
        #start_date = datetime(year=2025, month=2, day=1).date()
        #end_date = datetime.utcnow().date() - timedelta(days=2)  # Heute minus 2 Tage
        date_params = f"&start_date={start_date}&end_date={end_date}"

        # end_date = datetime.utcnow().date()
        # start_date = end_date - timedelta(days=14)
        # date_params = f"&start_date={start_date}&end_date={end_date}"
    else:
        base_url = "https://api.open-meteo.com/v1/forecast"
        date_params = "&forecast_days=16"

    lat_list = ",".join(str(row["latitude"]) for row in coords)
    lon_list = ",".join(str(row["longitude"]) for row in coords)

    return (
        f"{base_url}?latitude={lat_list}&longitude={lon_list}"
        f"{date_params}"
        f"&hourly={hourly_params}"
        "&models=icon_seamless"
        "&timezone=Europe/Berlin"
    )


# 🔁 JSON vertikalisieren
def normalize_and_verticalize(input_data):
    """
    Normalizes and verticalizes API Response data:
    - If the input is a JSON string, it converts it into a dict or a list.
    - If the JSON is a single dictionary, it converts it into a list.
    - If 'hourly' contains parallel lists, it verticalizes them into a list of dicts under 'hourly'.
    """
    import json

    if isinstance(input_data, str):
        input_data = json.loads(input_data)

    if isinstance(input_data, dict):
        input_data = [input_data]

    if not isinstance(input_data, list):
        raise ValueError(
            "Unexpected data structure: expected a dict, a list, or a valid JSON string."
        )

    transformed_data = []

    for entry in input_data:
        # Copy all the fields except "hourly"
        transformed_entry = {k: v for k, v in entry.items() if k != "hourly"}

        # Transform the "hourly" data, with consistency check
        hourly_data = entry["hourly"]
        keys = [
            "time",
            "temperature_2m",
            "rain",
            "cloud_cover",
            "precipitation",
            "apparent_temperature",
            "dew_point_2m",
            "pressure_msl",
            "windspeed_10m",
            "sunshine_duration",
        ]
        list_lengths = {k: len(hourly_data.get(k, [])) for k in keys}
        if len(set(list_lengths.values())) != 1:
            raise ValueError("Not all hourly values have the same length.")

        transformed_hourly = []
        for i in range(list_lengths["time"]):
            transformed_hourly.append(
                {
                    "time": hourly_data["time"][i],
                    "temperature_2m": hourly_data["temperature_2m"][i],
                    "rain": hourly_data["rain"][i],
                    "cloud_cover": hourly_data["cloud_cover"][i],
                    "precipitation": hourly_data["precipitation"][i],
                    "apparent_temperature": hourly_data["apparent_temperature"][i],
                    "dew_point_2m": hourly_data["dew_point_2m"][i],
                    "pressure_msl": hourly_data["pressure_msl"][i],
                    "windspeed_10m": hourly_data["windspeed_10m"][i],
                    "sunshine_duration": hourly_data["sunshine_duration"][i],
                }
            )

        transformed_entry["hourly"] = transformed_hourly
        transformed_data.append(transformed_entry)

    return transformed_data


# JSON in DB speichern
def store_response(table_name, json_data):
    insert_query = f"INSERT INTO {table_name} (daten) VALUES (%s)"
    try:
        # execute_query(insert_query, (json.dumps(json_data),))
        # print("Erfolgreich gespeichert.")
        transformed = normalize_and_verticalize(json_data)
        execute_query(insert_query, (json.dumps(transformed),))
        log_info(f"Transformierte Wetterdaten erfolgreich in {table_name} gespeichert.")
        return True
    except Exception as e:
        log_error(f"Fehler beim Speichern der Wetterdaten: {e}")
        return False

# Hauptfunktion
def run_forecast(case):
    log_info(f"Starte Forecast für: {case}")

    if case == "historisch":
        station_table = "wetterstation_hist"
        storage_table = "wetterdaten_hist"
        start = datetime(2016, 1, 1).date()
        end = datetime.utcnow().date() - timedelta(days=2)
        interval_days = 30 # 30 Tage pro Abschnitt
    elif case == "aktuell":
        station_table = "wetterstation_akt"
        storage_table = "vorhersage_akt"
    else:
        log_error("Ungültiger Fall. Nur 'historisch' oder 'aktuell' erlaubt.")
        return

    offset = 0
    limit = 50
    index = 1

    while True:
        coords = get_coordinates(station_table, offset, limit)
        if not coords:
            log_info("Alle Koordinaten wurden verarbeitet.")
            break

        if case == "historisch" :
            current_start = start
            while current_start <= end:
                current_end = min(current_start + timedelta(days=interval_days - 1), end)
                url = build_url(coords, case, current_start, current_end)     
                #url = build_url(coords, case)
                log_info(f"Anfrage {index} (Offset {offset})")
                
                try:
                    response = get_with_retry(url)  # von error_handler wegen fehler 429 too many request
            #response = requests.get(url)
                    if response.status_code == 200:
                        json_data = response.json()
                        success = store_response(storage_table, json_data)
                        if success: 
                            log_info(f"Gruppe {index} gespeichert: {current_start} bis {current_end}")
                        else:
                             log_warning(f"Gruppe {index} konnte nicht gespeichert werden.") 
                    else:
                        log_warning(f"HTTP Fehler: {response.status_code} bei Gruppe {index}")
                except Exception as e:
                    log_error(f"Ausnahme in Gruppe {index}: {e}")

                current_start = current_end + timedelta(days=1)
                index += 1

        else: 
            url = build_url(coords, case)
            log_info(f"Anfrage {index} (Offset {offset})")

            try: 

                response = get_with_retry(url)
                if response.status_code == 200:
                    json_data = response.json()
                    store_response(storage_table, json_data)
                    log_info(f"Gruppe {index} gespeichert.")
                else:
                    log_warning(f"HTTP Fehler: {response.status_code} bei Gruppe {index}")
            except Exception as e:
                log_error(f"Ausnahme in Gruppe {index}: {e}")


        offset += limit
        index += 1
