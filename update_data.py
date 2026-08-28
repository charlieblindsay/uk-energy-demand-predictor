from weather_config import UK_WEATHER_LOCATIONS
from WeatherDataLoader import WeatherDataLoader
from DemandDataLoader import DemandDataLoader
from DataLoader import DataLoader
from sklearn.tree import DecisionTreeRegressor
from DataTransformer import DataTransformer
from DemandDataFrameBuilder import DemandDataFrameBuilder
from CloudStorage import CloudStorage
from config import RANDOM_STATE


def main():
    weather_data_loader = WeatherDataLoader(
        weather_locations_dict=UK_WEATHER_LOCATIONS,
        metrics=[
            'temperature_2m',
            'relative_humidity_2m',
            'apparent_temperature'
        ]
    )

    demand_data_loader = DemandDataLoader()

    data_loader = DataLoader(
        weather_data_loader=weather_data_loader,
        demand_data_loader=demand_data_loader,
        num_months_historical_data=12
    )

    training_df = data_loader.get_historical_data_df()
    future_df_with_inputs = data_loader.get_input_df_for_forecasting(
        num_days_of_forecasting=217
    )
    X_future = future_df_with_inputs.to_numpy()

    data_transformer = DataTransformer()

    X_train, _, y_train, _ = data_transformer.get_train_test_data(
        df=training_df,
        target_column='ND',
        test_size=0.2
    )

    decision_tree = DecisionTreeRegressor(random_state=RANDOM_STATE)

    decision_tree.fit(X_train, y_train)

    future_predicted_demand = decision_tree.predict(X_future)

    demand_dataframe_builder = DemandDataFrameBuilder()

    demand_df = demand_dataframe_builder.build(
        historical_df_with_demand_data=training_df,
        future_df_without_demand_data=future_df_with_inputs,
        future_predicted_demand=future_predicted_demand
    )

    cloud_storage = CloudStorage()
    cloud_storage.save_data(df=demand_df)


if __name__ == '__main__':
    main()
