import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
import holidays
from datetime import datetime


class WeatherDataLoader:
	def __init__(
		self,
		weather_locations_dict,
		metrics
	):
		"""_summary_

		Args:
			weather_locations_dict (dict): _description_
			metrics (list[str]): _description_
			start_date (str): Of format "YYYY-MM-DD"
			end_date (str): Of format "YYYY-MM-DD"
		"""
		# Setup the Open-Meteo API client with cache and retry on error
		cache_session = requests_cache.CachedSession(
			'.cache',
			expire_after=3600
		)
		retry_session = retry(
			cache_session,
			retries=5,
			backoff_factor=0.2
		)
		self.openmeteo = openmeteo_requests.Client(session=retry_session)

		self.locations = [location for location in weather_locations_dict.keys()]
		self.latitudes = [value['latitude'] for (key, value) in weather_locations_dict.items()]
		self.longitudes = [value['longitude'] for (key, value) in weather_locations_dict.items()]

		self.metrics = metrics

	def _make_request_to_weather_forecasting_api(self, num_days_to_forecast):
		url = "https://seasonal-api.open-meteo.com/v1/seasonal"

		params = {
			"latitude": self.latitudes,
			"longitude": self.longitudes,
			"hourly": self.metrics,
			"forecast_days": num_days_to_forecast
		}

		responses = self.openmeteo.weather_api(url, params=params)

		return responses

	def _make_request_to_historical_weather_api(self, start_date, end_date):
		url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

		params = {
			"latitude": self.latitudes,
			"longitude": self.longitudes,
			"hourly": self.metrics,
			"models": "ukmo_seamless",
			"start_date": start_date,
			"end_date": end_date
		}

		responses = self.openmeteo.weather_api(url, params=params)

		return responses

	def _convert_responses_into_df(self, responses):
		hourly = responses[0].Hourly()

		hourly_data = {
			"date": pd.date_range(
				start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
				end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
				freq=pd.Timedelta(seconds=hourly.Interval()),
				inclusive="left"
			)
		}

		for location_index in range(len(self.locations)):
			hourly = responses[location_index].Hourly()

			for metric_index, metric in enumerate(self.metrics):
				metric_values = hourly.Variables(metric_index).ValuesAsNumpy()
				hourly_data[f'{metric}_{self.locations[location_index]}'] = metric_values

		df = pd.DataFrame(data=hourly_data)

		df['year'] = df['date'].apply(func=lambda x: x.year)
		df['month'] = df['date'].apply(func=lambda x: x.month)
		df['day'] = df['date'].apply(func=lambda x: x.day)
		df['hour'] = df['date'].apply(func=lambda x: x.hour)

		df['holiday'] = df['date'].apply(
			func=lambda date: date in holidays.country_holidays('UK')
		)
		df['day_of_week'] = df['date'].apply(
			func=lambda date: datetime.strptime(date.strftime('%Y-%m-%d'), '%Y-%m-%d').weekday()
		)

		df.drop(columns=['date'], inplace=True)

		return df

	def get_historical_weather_data_df(self, start_date, end_date):
		responses = self._make_request_to_historical_weather_api(
			start_date=start_date,
			end_date=end_date
		)

		return self._convert_responses_into_df(responses)

	def get_forecast_weather_data_df(self, num_days_to_forecast):
		responses = self._make_request_to_weather_forecasting_api(
			num_days_to_forecast
		)

		return self._convert_responses_into_df(responses)
