from weather_config import UK_WEATHER_LOCATIONS
from WeatherDataLoader import WeatherDataLoader
from DemandDataLoader import DemandDataLoader
from sklearn.tree import DecisionTreeRegressor
from DataTransformer import DataTransformer
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from google.cloud import storage
import pandas as pd
import io
from config import BUCKET_NAME


def main():
    weather_data_loader = WeatherDataLoader(
        weather_locations_dict=UK_WEATHER_LOCATIONS,
        metrics=[
            'temperature_2m',
            'relative_humidity_2m',
            'apparent_temperature'
        ]
    )

    datetime_twelve_months_ago = (datetime.now() - relativedelta(months=12))
    date_twelve_months_ago = datetime_twelve_months_ago.strftime("%Y-%m-%d")
    last_year = datetime_twelve_months_ago.strftime("%Y")

    datetime_yesterday = (datetime.now() - timedelta(days=1))
    date_yesterday = datetime_yesterday.strftime("%Y-%m-%d")
    this_year = datetime_yesterday.strftime("%Y")

    weather_df = weather_data_loader.get_historical_weather_data_df(
        start_date=date_twelve_months_ago,
        end_date=date_yesterday
    )

    demand_data_loader = DemandDataLoader()
    demand_df = demand_data_loader.get_historical_demand_data_df(
        years=[last_year, this_year]
    )

    df = pd.merge(
        left=weather_df,
        right=demand_df,
        how='inner',
        on=['year', 'month', 'day', 'hour']
    )

    data_transformer = DataTransformer()

    X_train, X_test, y_train, y_test = data_transformer.get_train_test_split(
        df=df,
        target_column='ND',
        test_size=0.2
    )

    decision_tree = DecisionTreeRegressor(random_state=42)

    decision_tree.fit(X_train, y_train)

    df['datetime'] = pd.to_datetime(
        df[['year', 'month', 'day', 'hour']]
    )
    max_datetime = df['datetime'].max()

    df_weather_interim = weather_data_loader.get_historical_weather_data_df(
        start_date=max_datetime.strftime('%Y-%m-%d'),
        end_date=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') 
    )

    df_weather_future = weather_data_loader.get_forecast_weather_data_df(
        num_days_to_forecast=217
    )

    df_weather_for_forecasting = pd.concat([
        df_weather_interim,
        df_weather_future
    ])

    X_future = df_weather_for_forecasting.to_numpy()

    y_future_predict = decision_tree.predict(X_future)

    df_dict = {
        'datetime': [],
        'demand': [],
        'predicted': []
    }

    df_weather_for_forecasting['datetime'] = pd.to_datetime(
        df_weather_for_forecasting[['year', 'month', 'day', 'hour']]
    )

    for i in range(df.shape[0]):
        df_dict['datetime'].append(
            df.iloc[i]['datetime']
        )
        df_dict['demand'].append(
            df.iloc[i]['ND']
        )
        df_dict['predicted'].append(False)

    for i in range(df_weather_for_forecasting.shape[0]):
        df_dict['datetime'].append(
            df_weather_for_forecasting.iloc[i]['datetime']
        )
        df_dict['demand'].append(
            y_future_predict[i]
        )
        df_dict['predicted'].append(True)

    historical_and_predicted_demand_df = pd.DataFrame(df_dict).set_index("datetime")

    buffer = io.BytesIO()
    historical_and_predicted_demand_df.to_parquet(buffer)

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob("predictions.parquet")

    blob.upload_from_string(buffer.getvalue())


if __name__ == '__main__':
    main()
