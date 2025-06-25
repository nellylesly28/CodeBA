import requests
from bs4 import BeautifulSoup
from db_pool import execute_query


# Funktion zum Abrufen historischer Wetterstationsdaten vom DWD (Textdatei)
def get_historic_station():
    url = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/KL_Tageswerte_Beschreibung_Stationen.txt"
    response = requests.get(url)
    response.raise_for_status()  # Löst eine Exception aus, wenn der Abruf fehlschlägt

    lines = response.text.split("\n")
    historic_station = []

    for line in lines:
        if "geoBreite" in line:
            continue  # Überspringe Header-Zeile

        fields = line.split()
        if len(fields) >= 6:
            try:
                station_id = fields[0]
                # Umwandlung der Koordinaten ins float-Format, dabei Kommas durch Punkte ersetzen
                latitude = float(fields[4].replace(",", "."))
                longitude = float(fields[5].replace(",", "."))
                station_name = " ".join(fields[6:-3])
                historic_station.append((station_id, latitude, longitude, station_name))
            except ValueError:
                continue  ## Zeilen mit ungültigen Werten überspringen
    return historic_station

#Funktion zum Abrufen aktueller Wetterstationsdaten vom DWD (HTML-Seite)
def get_current_station():
    url = "https://www.dwd.de/DE/leistungen/klimadatendeutschland/statliste/statlex_html.html?view=nasPublication&nn=16102"
    
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")
    current_station = []

    table = soup.find("table")
    if not table:
        print("Tabelle nicht gefunden!")
        return []

    rows = table.find_all("tr") #[1:]

    for row in rows[1:]: #skip header row # Erste Zeile ist die Tabellenüberschrift
        cols = row.find_all("td")
        if len(cols) >= 6:
            try:
                station_id = cols[1].text.strip()
                station_name = cols[0].text.strip()
                latitude = float(cols[4].text.strip().replace(",", "."))
                longitude = float(cols[5].text.strip().replace(",", "."))
                current_station.append((station_id, station_name, latitude, longitude))
            except ValueError:
                continue
    return current_station

# Funktion zur Speicherung der abgerufenen Stationsdaten in der Datenbank
def save_to_database(historic_station, current_station):
    insert_hist_query = """
        INSERT INTO wetterstation_hist (station_id, latitude, longitude, station_name)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            latitude = VALUES(latitude),
            longitude = VALUES(longitude),
            station_name = VALUES(station_name)
    """
    
    insert_current_query = """
        INSERT INTO wetterstation_akt (station_id, station_name, latitude, longitude)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            station_name = VALUES(station_name),
            latitude = VALUES(latitude),
            longitude = VALUES(longitude)
    """

    execute_query(insert_hist_query, historic_station)
    execute_query(insert_current_query, current_station)
    print("Wetterstationen gespeichert oder aktualisiert.")


def run_station_update():
    try:
        historic = get_historic_station()
        current = get_current_station()
        save_to_database(historic, current)
    except Exception as e:
        print(f"Fehler bei Station-Update: {e}")
