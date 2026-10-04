# Hong Kong Rainfall Fingerprint — 2025
# 香港降雨指纹 — 2025

I chose Hong Kong rainfall for this project. I want to see how rain is spread
through a year, using a circular plot where longer bars mean more rain.


The [data](https://data.weather.gov.hk/weatherAPI/cis/csvfile/HKO/ALL/daily_HKO_RF_ALL.csv)
comes from the Hong Kong Observatory station. Each row records a date, daily
rainfall in millimetres, and a completeness flag. The file has 49,492 records;
I will use the 365 days in 2025. This is one station, not a city-wide average.

There are 53 `Trace` days, meaning less than 0.05 mm of rain. I will keep these
separate from days with no rain.


The raw file is saved unchanged. The first plot is next.
