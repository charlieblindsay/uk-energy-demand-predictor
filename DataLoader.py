from datetime import datetime, timedelta
import pandas as pd
from dateutil.relativedelta import relativedelta
from WeatherDataLoader import WeatherDataLoader
from DemandDataLoader import DemandDataLoader


class DataLoader:
    def __init__(
        self,
        weather_data_locations,
        weather_metrics,
        num_months_data
    ):
        self.weather_data_loader = WeatherDataLoader(
            weather_locations_dict=weather_data_locations,
            metrics=weather_metrics
        )
        self.demand_data_loader = DemandDataLoader()
        self.num_months_data = num_months_data

    def get_historical_data_df(self):
        start_datetime = (datetime.now() - relativedelta(months=self.num_months_data))
        start_date = start_datetime.strftime("%Y-%m-%d")
        start_year = start_datetime.strftime("%Y")

        yesterday_datetime = (datetime.now() - timedelta(days=1))
        yesterday_date = yesterday_datetime.strftime("%Y-%m-%d")
        yesterday_year = yesterday_datetime.strftime("%Y")

        weather_df = self.weather_data_loader.get_historical_weather_data_df(
            start_date=start_date,
            end_date=yesterday_date
        )

        demand_df = self.demand_data_loader.get_historical_demand_data_df(
            years=[start_year, yesterday_year]
        )

        df = pd.merge(
            left=weather_df,
            right=demand_df,
            how='inner',
            on=['year', 'month', 'day', 'hour']
        )

        return df

    def get_input_df_for_forecasting(self, num_days_of_forecasting):
        historical_df = self.get_historical_data_df()

        max_datetime = pd.to_datetime(
            historical_df[['year', 'month', 'day', 'hour']]
        ).max()

        df_weather_interim = self.weather_data_loader.get_historical_weather_data_df(
            start_date=max_datetime.strftime('%Y-%m-%d'),
            end_date=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        )

        df_weather_future = self.weather_data_loader.get_forecast_weather_data_df(
            num_days_to_forecast=num_days_of_forecasting
        )

        df_weather_for_forecasting = pd.concat([
            df_weather_interim,
            df_weather_future
        ])

        return df_weather_for_forecasting
