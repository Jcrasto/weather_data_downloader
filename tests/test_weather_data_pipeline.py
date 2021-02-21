import argparse
import json
import os

import pandas as pd
import scripts.weather_data_pipeline as weather_data_pipeline

abspath = os.path.abspath(__file__)
os.chdir(os.path.dirname(abspath))


def test_build_request_location_df():
    args = argparse.Namespace()
    args.city = "Houston"
    args.state = None
    args.top_cities = None

    result = weather_data_pipeline.build_request_location_df(args)
    expected = pd.DataFrame({'city': ['Houston'],
                             'latitude': [29.7604267],
                             'longitude': [-95.3698028],
                             'state': ['Texas']})
    pd.testing.assert_frame_equal(result, expected)

    args = argparse.Namespace()
    args.city = None
    args.state = "Texas"
    args.top_cities = 5
    result = weather_data_pipeline.build_request_location_df(args)
    expected = pd.DataFrame({
        'city': ['Houston', 'San Antonio', 'Dallas', 'Austin', 'Fort Worth'],
        'latitude': [29.7604267, 29.4241219, 32.7766642, 30.267153, 32.7554883],
        'longitude': [-95.3698028,
                      -98.49362819999999,
                      -96.79698789999999,
                      -97.7430608,
                      -97.3307658],
        'state': ['Texas', 'Texas', 'Texas', 'Texas', 'Texas']}
    )
    pd.testing.assert_frame_equal(result, expected)


def test_parse_daily():
    mock_response = '''{"lat":40.7128,"lon":-74.0059,"daily":[{"dt":1613667600,"sunrise":1613648749,"sunset":1613687660,"temp":{"day":26.47,"min":26.19,"max":29.3,"night":27.3,"eve":28.06,"morn":26.19},"feels_like":{"day":17.78,"night":17.56,"eve":15.67,"morn":14.72},"pressure":1029,"humidity":93,"dew_point":24.69,"wind_speed":7.43,"wind_deg":46,"weather":[{"id":601,"main":"Snow","description":"snow","icon":"13d"}],"clouds":100,"pop":1,"snow":6.83,"uvi":1.28}]}'''
    json_obj = json.loads(mock_response)
    result = weather_data_pipeline.parse_daily(json_obj)
    expected = pd.DataFrame({'dt': [pd.Timestamp('2021-02-18 17:00:00')],
                             'sunrise': [pd.Timestamp('2021-02-18 11:45:49')],
                             'sunset': [pd.Timestamp('2021-02-18 22:34:20')],
                             'feels_like': [{'day': 17.78, 'night': 17.56, 'eve': 15.67, 'morn': 14.72}],
                             'pressure': [1029],
                             'humidity': [93],
                             'dew_point': [24.69],
                             'wind_speed': [7.43],
                             'wind_deg': [46],
                             'weather': [[{'id': 601,
                                           'main': 'Snow',
                                           'description': 'snow',
                                           'icon': '13d'}]],
                             'clouds': [100],
                             'pop': [1],
                             'snow': [6.83],
                             'uvi': [1.28],
                             'day': [26.47],
                             'min': [26.19],
                             'max': [29.3],
                             'night': [27.3],
                             'eve': [28.06],
                             'morn': [26.19],
                             'lat': [40.7128],
                             'lon': [-74.0059]})
    pd.testing.assert_frame_equal(result, expected)
