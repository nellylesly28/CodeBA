from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt
from db_pool import execute_query  # dein Connection-Pool Code

# 1️⃣ Alle eindeutigen Stationen holen
stations_query = "SELECT DISTINCT station_id FROM dwd_hist_wetterdaten;"
stations = execute_query(stations_query, fetch=True)

if not stations:
    print("⚠️ Keine Stationen gefunden!")
    exit()

# 2️⃣ Für jede Station die Prognose berechnen
for station in stations:
    station_id = station['station_id']
    print(f"\n📍 Prognose für Station: {station_id}")

    # Historische Daten für diese Station holen
    data_query = """
        SELECT 
            date_hour AS ds, 
            apparent_temperatur AS y
        FROM dwd_hist_wetterdaten
        WHERE station_id = %s
        ORDER BY ds;
    """
    rows = execute_query(data_query, params=(station_id,), fetch=True)

    if not rows:
        print(f"⚠️ Keine Daten für Station {station_id}")
        continue

    # In DataFrame
    df = pd.DataFrame(rows)
    df['ds'] = pd.to_datetime(df['ds'])
    # NULL oder 'null' in float konvertieren
    df['y'] = pd.to_numeric(df['y'], errors='coerce')  # Wandelt ungültige Werte in NaN
    df = df.dropna(subset=['y'])  # Zeilen mit NaN löschen

    if df.empty:
        print(f"⚠️ Keine gültigen Temperaturdaten für Station {station_id}")
        continue
    # Prophet Modell trainieren
    model = Prophet()
    model.fit(df)

    # 10 Jahre Prognose
    future = model.make_future_dataframe(periods=3650, freq='D')
    forecast = model.predict(future)

    # Ergebnisse in Konsole
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head(10))

    # Diagramm
    fig = model.plot(forecast)
    plt.title(f"Forecast Station {station_id}")
    plt.show()
