I chose Hong Kong rainfall for this project. I want to see how rain is spread
through a year, using a circular plot where longer bars mean more rain.
Days run clockwise from January at the top.


The [data](https://data.weather.gov.hk/weatherAPI/cis/csvfile/HKO/ALL/daily_HKO_RF_ALL.csv)
comes from the Hong Kong Observatory station. Each row records a date, daily
rainfall in millimetres, and a completeness flag. The file has 49,492 records;
The plot uses the 365 days in 2025. This is one station, not a city-wide average.

There are 53 `Trace` days, meaning less than 0.05 mm of rain. Small dots show
these days; days with no rain have no bar.


Most of the longer bars fall between July and September. The chart shows daily
totals, so it cannot tell us when the rain fell within a day. The raw file is
saved unchanged.
