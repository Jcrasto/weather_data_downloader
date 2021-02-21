import argparse
import datetime
import json
import os

import pandas as pd
import requests


def build_request_location_df(args):
    """
    :param args: city, state, and top_cities as defined in the README
    :return: a dataframe with only the subset of columns for which requests will be made
    """
    city = args.city
    state = args.state
    top_cities = args.top_cities

    location_mappings = pd.read_json(r"../data/largest_cities.json").drop(
        ["growth_from_2000_to_2013", "population", "rank"], axis=1
    )

    if city:
        request_locations = location_mappings[location_mappings["city"] == city]
    elif state:
        request_locations = location_mappings[location_mappings["state"] == state].head(
            top_cities
        )
    else:
        request_locations = location_mappings.loc[0:top_cities]

    request_locations = request_locations.reset_index(drop=True)
    return request_locations


def read_previous_csv(timeframe):
    """
    :param timeframe: hourly or daily, the two files that forecast csvs are generated for
    :return: a dataframe of the existing data in the data directory to append to or an empty dataframe
    """
    if os.path.exists(r"../data/{}_forecast.csv".format(timeframe)):
        if os.stat(r"../data/{}_forecast.csv".format(timeframe)).st_size != 0:
            df = pd.read_csv(r"../data/{}_forecast.csv".format(timeframe))
    else:
        df = pd.DataFrame()
    return df


def build_request(row):
    """
    :param row: row in a dataframe from which to build the request url
    :return: the request url
    """
    api_key = os.getenv("OPENWEATHERMAP_APIKEY")
    if api_key == None:
        raise Exception(
            "Please set OPENWEATHERMAP_APIKEY Property as described in README"
        )
    return "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&units=imperial&appid={}".format(
        str(row["latitude"]), str(row["longitude"]), api_key
    )


def parse_daily(json_obj):
    """
    :param json_obj: json.loads(response.content) from the response from the api
    :return: a dataframe with the values in the json object parsed
    """
    daily_df = pd.DataFrame.from_dict(json_obj["daily"])
    daily_df["dt"] = pd.to_datetime(daily_df["dt"], unit="s")
    daily_df["sunrise"] = pd.to_datetime(daily_df["sunrise"], unit="s")
    daily_df["sunset"] = pd.to_datetime(daily_df["sunset"], unit="s")
    daily_df = daily_df.drop("temp", axis=1).join(
        pd.DataFrame(daily_df.temp.values.tolist())
    )
    daily_df["lat"] = json_obj["lat"]
    daily_df["lon"] = json_obj["lon"]
    return daily_df


def parse_hourly(json_obj):
    """
    :param json_obj: json.loads(response.content) from the response from the api
    :return: a dataframe with the values in the json object parsed
    """
    hourly_df = pd.DataFrame.from_dict(json_obj["hourly"])
    hourly_df["dt"] = pd.to_datetime(hourly_df["dt"], unit="s")
    hourly_df["lat"] = json_obj["lat"]
    hourly_df["lon"] = json_obj["lon"]
    return hourly_df


def update_forecasts(daily_fcst, hourly_fcst, request_locations):
    """
    :param daily_fcst: dataframe either empty or containing the data in ../data/daily_forecast
    :param hourly_fcst: dataframe either empty or containing the data in ../data/hourly_forecast
    :param request_locations: dataframe containing the urls for requests
    :return: daily_fcst and hourly_fcst, two dataframes with the new data requested
    """
    for i in range(request_locations.shape[0]):  # len(request_locations)
        row = request_locations.loc[i]
        create_ts = datetime.datetime.utcnow().strftime("%d-%b-%Y %H:%M:%S.%f")
        resp = requests.get(row["request_url"])
        resp.raise_for_status()
        json_obj = json.loads(resp.content)
        daily_df = parse_daily(json_obj)
        hourly_df = parse_hourly(json_obj)
        daily_df["create_ts"] = create_ts
        hourly_df["create_ts"] = create_ts
        daily_df["city"] = row["city"]
        hourly_df["city"] = row["city"]
        daily_fcst = daily_fcst.append(daily_df)
        hourly_fcst = hourly_fcst.append(hourly_df)
    return daily_fcst, hourly_fcst


def main(args):
    """
    :param args: city, state, and top_cities as defined in the README
    :output: ../data/daily_forecast.csv and ../data/hourly_forecast.csv
    """
    request_locations = build_request_location_df(args)
    request_locations["request_url"] = request_locations.apply(build_request, axis=1)

    daily_fcst = read_previous_csv('daily')
    hourly_fcst = read_previous_csv('hourly')

    daily_fcst, hourly_fcst = update_forecasts(
        daily_fcst, hourly_fcst, request_locations
    )

    daily_fcst.to_csv("../data/daily_forecast.csv", index=False)
    hourly_fcst.to_csv("../data/hourly_forecast.csv", index=False)


if __name__ == "__main__":
    # set path as the directory of the script so data directory can be referred to with relative path
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--city", help="The city for which you want data", type=str, required=False
    )
    parser.add_argument(
        "--state", help="The state for which you want data", type=str, required=False
    )
    parser.add_argument(
        "--top_cities",
        help="Number of cities for which you want data",
        type=int,
        required=False,
        default=5
    )
    args = parser.parse_args()

    main(args)
