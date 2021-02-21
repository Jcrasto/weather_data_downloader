# Weather Data Downloader

## Description
The script weather_data_pipeline.py sends a request to the OpenWeatherMap one-call API: https://openweathermap.org/api/one-call-api#data.
The data from the response that we are interested in is the hourly forecast for 48 hours and daily forecast for 7 days.
This data will be used to update or create the daily_forecast and hourly_forecast files.


# Getting Started

## Set up environment variable for API
Set the environment variable for the API key for the openweathermap api.

If running from the command line run the line below to create the variable.

`
export OPENWEATHERMAP_APIKEY=
`

## Project Structure

At the base project directory there should be two folders, `scripts` and `data`.

The `scripts` folder contains the `weather_data_pipeline.py` script.

The `data` folder should contain a json called `largest_cities.json`.
If the `largest_cities.json` file does not exist you will need to [download](https://gist.github.com/Miserlou/c5cd8364bf9b2420bb29) it and place it in the data folder to source city coordinates.

## Running the Script
When you run the script you pass into the main function which forecasts you want to download.

```python weather_data_pipeline.py```

No arguments will mean the script by default will download the weather forecasts for the top 5 biggest cities in the US by population (based on the json).

```python weather_data_pipeline.py --city "San Diego"``` 

The `city` parameter will mean the script will ignore all other parameters and only download data for the city specified, if the city does not exist the script will fail

```python weather_data_pipeline.py --state California```

The `state` parameter will mean the script will search for cities within that state to download data for.
 The number of cities within the state is specified by the `top_cities` parameter, which is 5 by default
 
```python weather_data_pipeline.py --top_cities 5```

The `top_cities` parameter will mean the script will download that number of forecasts with cities starting from the greatest
population in the json to the least. This parameter can be used in conjunction with the `state` parameter, but will be ignored for 
the `city` parameter, and is 5 by default 



### Parameters

```
  --top_cities TOP_CITIES  Number of cities for which you want data
  --city CITY              The city for which you want data
  --state STATE            The state for which you want data
```
## Output
The output files will be in the data directory and will be `daily_fcst.csv` and `hourly_fcst.csv`.  
