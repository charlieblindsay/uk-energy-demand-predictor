from weather_config import UK_WEATHER_LOCATIONS
from WeatherDataLoader import WeatherDataLoader
from DemandDataLoader import DemandDataLoader
from sklearn.tree import DecisionTreeRegressor
from DataTransformer import DataTransformer
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import numpy as np


def main():
    weather_data_loader = WeatherDataLoader(
        weather_locations_dict=UK_WEATHER_LOCATIONS,
        metrics=[
            'temperature_2m',
            'relative_humidity_2m',
            'apparent_temperature'
        ]
    )

    weather_df = weather_data_loader.get_historical_weather_data_df(
        start_date='2026-05-01',
        end_date='2026-07-01'
    )

    demand_data_loader = DemandDataLoader()
    demand_df = demand_data_loader.get_historical_demand_data_df(
        years=['2026']
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

    y_predict = decision_tree.predict(X_test)

    print(sum([
        (y_predict[i] - y_test[i]) ** 2 for i in range(len(y_predict))
    ]) / len(y_predict))

    df_future = weather_data_loader.get_forecast_weather_data_df(
        num_days_to_forecast=217
    )

    print(df_future.columns)

    X_future = df_future.to_numpy()

    y_future_predict = decision_tree.predict(X_future)

    X_future_new = np.ndarray(shape=(X_future.shape[0], X_future.shape[1] + 1))

    for i in range(X_future_new.shape[0]):
        for j in range(X_future_new.shape[1]):
            if j == X_future_new.shape[1] - 1:
                X_future_new[i, j] = y_future_predict[i]
            else:
                X_future_new[i, j] = X_future[i, j]

    print(X_future_new[0])

    print(df_future.columns)

    df_dict = {
        'datetime': [],
        'predictions': []
    }

    for i in range(df_future.shape[0]):
        year = df_future.iloc[i]['year']
        month = df_future.iloc[i]['month']
        day = df_future.iloc[i]['day']
        hour = df_future.iloc[i]['hour']
        demand_prediction = y_future_predict[i]

        df_dict['datetime'].append(
            datetime(year=year, month=month, day=day, hour=hour)
        )
        df_dict['predictions'].append(
            demand_prediction
        )

    df = pd.DataFrame(df_dict).set_index("datetime")

    print(df)

    start_date = st.date_input(
        label='start_date',
        min_value=datetime.now(),
        max_value=datetime.now() + timedelta(days=217)
    )
    end_date = st.date_input(
        label='end_date',
        min_value=datetime.now(),
        max_value=datetime.now() + timedelta(days=217)
    )

    df_filtered = df.loc[start_date:end_date + timedelta(days=1)]

    st.line_chart(df_filtered)


if __name__ == '__main__':
    main()
