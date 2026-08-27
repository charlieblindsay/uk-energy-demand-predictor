from weather_config import UK_WEATHER_LOCATIONS
from WeatherDataLoader import WeatherDataLoader
from DemandDataLoader import DemandDataLoader
from sklearn.tree import DecisionTreeRegressor
from DataTransformer import DataTransformer
from datetime import datetime, timedelta
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

    date_twelve_months_ago = str(datetime.now() - timedelta(days=12 * 30)).split(' ')[0]
    last_year = date_twelve_months_ago.split('-')[0]

    yesterday_date = str(datetime.now() - timedelta(days=1)).split(' ')[0]
    this_year = yesterday_date.split('-')[0]

    weather_df = weather_data_loader.get_historical_weather_data_df(
        start_date=date_twelve_months_ago,
        end_date=yesterday_date
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

    df_future = weather_data_loader.get_forecast_weather_data_df(
        num_days_to_forecast=217
    )

    X_future = df_future.to_numpy()

    y_future_predict = decision_tree.predict(X_future)

    df_dict = {
        'datetime': [],
        'demand': []
    }

    for i in range(df.shape[0]):
        year = df.iloc[i]['year']
        month = df.iloc[i]['month']
        day = df.iloc[i]['day']
        hour = df.iloc[i]['hour']
        demand = df.iloc[i]['ND']

        df_dict['datetime'].append(
            datetime(year=year, month=month, day=day, hour=hour)
        )
        df_dict['demand'].append(
            demand
        )

    for i in range(df_future.shape[0]):
        year = df_future.iloc[i]['year']
        month = df_future.iloc[i]['month']
        day = df_future.iloc[i]['day']
        hour = df_future.iloc[i]['hour']
        demand_prediction = y_future_predict[i]

        df_dict['datetime'].append(
            datetime(year=year, month=month, day=day, hour=hour)
        )
        df_dict['demand'].append(
            demand_prediction
        )

    historical_and_predicted_demand_df = pd.DataFrame(df_dict).set_index("datetime")

    buffer = io.BytesIO()
    historical_and_predicted_demand_df.to_parquet(buffer)

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob("predictions.parquet")

    blob.upload_from_string(buffer.getvalue())


if __name__ == '__main__':
    main()
