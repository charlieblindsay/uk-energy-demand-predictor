from DataLoader import DataLoader
from DataSplitter import DataSplitter
from DemandDataFrameBuilder import DemandDataFrameBuilder
from CloudStorage import CloudStorage
from DemandModel import DemandModel
from config import RANDOM_STATE
from config import WEATHER_METRICS, UK_WEATHER_LOCATIONS
from config import NUM_MONTHS_HISTORICAL_TRAINING_DATA
from config import NUM_DAYS_OF_FORECASTING
from config import TEST_SIZE
from config import COLUMN_TO_PREDICT


def main():
    data_loader = DataLoader(
        weather_data_locations=UK_WEATHER_LOCATIONS,
        weather_metrics=WEATHER_METRICS,
        num_months_data=NUM_MONTHS_HISTORICAL_TRAINING_DATA
    )

    training_df = data_loader.get_historical_data_df()
    future_df_with_inputs = data_loader.get_input_df_for_forecasting(
        num_days_of_forecasting=NUM_DAYS_OF_FORECASTING
    )
    X_future = future_df_with_inputs.to_numpy()

    data_transformer = DataSplitter()

    X_train, _, y_train, _ = data_transformer.get_train_test_data(
        df=training_df,
        target_column=COLUMN_TO_PREDICT,
        test_size=TEST_SIZE
    )

    model = DemandModel(random_state=RANDOM_STATE)
    model.fit(X_train=X_train, y_train=y_train)
    future_predicted_demand = model.predict(X_future)

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
