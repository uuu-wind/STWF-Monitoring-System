import openmeteo_requests
import json
import os

import pandas as pd
import requests_cache
from retry_requests import retry

class Weather:
    def __init__(self, config_file_path="config.json"):
        self.config_file_path = config_file_path
        self.config = self._load_config()
        
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)
        
        self.url = "https://api.open-meteo.com/v1/forecast"
    
    def _load_config(self):
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"latitude": 30.2936, "longitude": 120.1614, "turbine_orientation": ""}
    
    def get_weather(self, forecast_days=2):
        params = {
            "latitude": self.config.get("latitude", 30.2936),
            "longitude": self.config.get("longitude", 120.1614),
            "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "surface_pressure"],
            "timezone": "Asia/Shanghai",
            "forecast_days": forecast_days,
        }
        
        responses = self.openmeteo.weather_api(self.url, params=params)
        response = responses[0]
        
        # print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        # print(f"Elevation {response.Elevation()} m asl")
        # print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        # print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")
        
        hourly = response.Hourly()
        
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_convert("Asia/Shanghai"),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True).tz_convert("Asia/Shanghai"),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
        }
        
        hourly_data["temperature_2m"] = hourly.Variables(0).ValuesAsNumpy()
        hourly_data["relative_humidity_2m"] = hourly.Variables(1).ValuesAsNumpy()
        hourly_data["wind_speed_10m"] = hourly.Variables(2).ValuesAsNumpy()
        hourly_data["wind_direction_10m"] = hourly.Variables(3).ValuesAsNumpy()
        hourly_data["surface_pressure"] = hourly.Variables(4).ValuesAsNumpy()
        
        hourly_dataframe = pd.DataFrame(data=hourly_data)
        
        return hourly_dataframe

    def get_past_weather(self):
        params = {
            "latitude": self.config.get("latitude", 30.2936),
            "longitude": self.config.get("longitude", 120.1614),
            "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m", "surface_pressure"],
            "timezone": "Asia/Shanghai",
            "past_days": 7,
            "forecast_days": 0
        }

        responses = self.openmeteo.weather_api(self.url, params=params)
        response = responses[0]

        hourly = response.Hourly()
        
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_convert("Asia/Shanghai"),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True).tz_convert("Asia/Shanghai"),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
        }

        hourly_data["temperature_2m"] = hourly.Variables(0).ValuesAsNumpy()
        hourly_data["relative_humidity_2m"] = hourly.Variables(1).ValuesAsNumpy()
        hourly_data["wind_speed_10m"] = hourly.Variables(2).ValuesAsNumpy()
        hourly_data["wind_direction_10m"] = hourly.Variables(3).ValuesAsNumpy()
        hourly_data["surface_pressure"] = hourly.Variables(4).ValuesAsNumpy()
        
        hourly_dataframe = pd.DataFrame(data=hourly_data)
        
        return hourly_dataframe

if __name__ == "__main__":
    weather = Weather()
    print("\nHourly data\n")
    print(weather.get_past_weather())