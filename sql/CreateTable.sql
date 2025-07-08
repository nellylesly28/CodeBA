USE weather_data;
#Tabelle um Historische Wetterstation Koordinaten zu speicher
CREATE TABLE IF NOT EXISTS wetterstation_hist (
    station_id varchar(20) PRIMARY KEY,
    station_name TEXT,
    latitude DECIMAL(8, 5) NOT NULL,
    longitude DECIMAL(8, 5) NOT NULL
);
# Tabelle um aktuelle Wetterstation Koordinaten zu speichern
CREATE TABLE IF NOT EXISTS wetterstation_akt (
    station_id varchar(20) PRIMARY KEY,
    station_name TEXT,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL
);

#Tabelle um aktuelle Wettervorhersage zu speichern
 CREATE TABLE IF NOT EXISTS vorhersage_akt (
                 id INT PRIMARY KEY AUTO_INCREMENT,
                 abfragezeit TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                daten JSON
);

#Tabelle um Historische Wetterdaten zu speichern
CREATE TABLE IF NOT EXISTS wetterdaten_hist (
                 id INT PRIMARY KEY AUTO_INCREMENT,
                 abfragezeit TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                daten JSON
);
                
