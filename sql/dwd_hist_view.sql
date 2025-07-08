use weather_data;

CREATE OR REPLACE VIEW dwd_hist_view AS
SELECT
  v.id,
  v.abfragezeit,
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
FROM wetterdaten_hist v
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
JOIN JSON_TABLE(
  eintrag.hourly, '$.time[*]'
  COLUMNS (
    `index` FOR ORDINALITY,
    time VARCHAR(50) PATH '$'
  )
) AS stunde
JOIN JSON_TABLE(
  eintrag.hourly, '$.temperature_2m[*]'
  COLUMNS (`index` FOR ORDINALITY, value DOUBLE PATH '$')
) AS temperatur USING (`index`)
JOIN JSON_TABLE(
  eintrag.hourly, '$.windspeed_10m[*]'
  COLUMNS (`index` FOR ORDINALITY, value DOUBLE PATH '$')
) AS wind USING (`index`)
JOIN JSON_TABLE(
  eintrag.hourly, '$.sunshine_duration[*]'
  COLUMNS (`index` FOR ORDINALITY, value DOUBLE PATH '$')
) AS sonnenschein USING (`index`)
JOIN JSON_TABLE(
  eintrag.hourly, '$.precipitation[*]'
  COLUMNS (`index` FOR ORDINALITY, value DOUBLE PATH '$')
) AS niederschlag USING (`index`)
JOIN JSON_TABLE(
  eintrag.hourly, '$.pressure_msl[*]'
  COLUMNS (`index` FOR ORDINALITY, value DOUBLE PATH '$')
) AS druck USING (`index`)
JOIN JSON_TABLE(
  eintrag.hourly, '$.dew_point_2m[*]'
  COLUMNS (`index` FOR ORDINALITY, value DOUBLE PATH '$')
) AS taupunkt USING (`index`);

select * from dwd_hist_view;
SELECT abfragezeit FROM dwd_hist_view ORDER BY abfragezeit DESC LIMIT 5;
SELECT * FROM stundenweise_vorhersage ORDER BY abfragezeit DESC LIMIT 10;
