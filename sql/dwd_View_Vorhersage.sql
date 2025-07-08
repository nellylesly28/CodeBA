use weather_data;
CREATE OR REPLACE VIEW dwd_vorhersage AS
SELECT
  v.abfragezeit,
  w.station_id,
  w.station_name,
  eintrag.ord AS objekt_index,
  eintrag.latitude,
  eintrag.longitude,
  eintrag.timezone,
  eintrag.elevation,
  stunde.`index`,
  stunde.time,
  temperatur.value       AS temperature_2m,
  wind.value             AS windspeed_10m,
  sonnenschein.value     AS sunshine_duration,
  niederschlag.value     AS precipitation,
  druck.value            AS pressure_msl,
  taupunkt.value         AS dew_point_2m
FROM vorhersage_akt v
 JOIN JSON_TABLE(
  v.daten, '$[*]'
  COLUMNS (
    ord FOR ORDINALITY,
    latitude DOUBLE PATH '$.latitude',
    longitude DOUBLE PATH '$.longitude',
    timezone VARCHAR(100) PATH '$.timezone',
    elevation DOUBLE PATH '$.elevation',
    hourly JSON PATH '$.hourly'
  )
) AS eintrag
LEFT JOIN wetterstation_akt w
  ON w.latitude = eintrag.latitude AND w.longitude = eintrag.longitude
JOIN JSON_TABLE(
  eintrag.hourly, '$.time[*]'
  COLUMNS (
    `index` FOR ORDINALITY,
    time VARCHAR(50) PATH '$'
  )
) AS stunde
LEFT JOIN JSON_TABLE(
  eintrag.hourly, '$.temperature_2m[*]'
  COLUMNS (`index` FOR ORDINALITY, value DOUBLE PATH '$')
) AS temperatur USING (`index`)
LEFT JOIN JSON_TABLE(
  eintrag.hourly, '$.windspeed_10m[*]'
  COLUMNS (`index` FOR ORDINALITY, value DOUBLE PATH '$')
) AS wind USING (`index`)
LEFT JOIN JSON_TABLE(
  eintrag.hourly, '$.sunshine_duration[*]'
  COLUMNS (`index` FOR ORDINALITY, value DOUBLE PATH '$')
) AS sonnenschein USING (`index`)
LEFT JOIN JSON_TABLE(
  eintrag.hourly, '$.precipitation[*]'
  COLUMNS (`index` FOR ORDINALITY, value DOUBLE PATH '$')
) AS niederschlag USING (`index`)
LEFT JOIN JSON_TABLE(
  eintrag.hourly, '$.pressure_msl[*]'
  COLUMNS (`index` FOR ORDINALITY, value DOUBLE PATH '$')
) AS druck USING (`index`)
LEFT JOIN JSON_TABLE(
  eintrag.hourly, '$.dew_point_2m[*]'
  COLUMNS (`index` FOR ORDINALITY, value DOUBLE PATH '$')
) AS taupunkt USING (`index`);

SELECT * FROM dwd_vorhersage WHERE abfragezeit = '2025-06-22 22:26:19';
SELECT abfragezeit FROM vorhersage_akt ORDER BY abfragezeit DESC LIMIT 5;
SELECT * FROM dwd_vorhersage ORDER BY abfragezeit DESC LIMIT 10;
SELECT * FROM dwd_vorhersage;
select * from vorhersage_akt;
select * from wetterstation_akt;