import pytest
from DemandModel import DemandModel
from DataLoader import DataLoader
from DataSplitter import DataSplitter

from config import UK_WEATHER_LOCATIONS
from config import WEATHER_METRICS
from config import NUM_MONTHS_HISTORICAL_TRAINING_DATA
from config import COLUMN_TO_PREDICT
from config import TEST_SIZE
from config import RANDOM_STATE


@pytest.fixture
def data_splits():
    data_loader = DataLoader(
        weather_data_locations=UK_WEATHER_LOCATIONS,
        weather_metrics=WEATHER_METRICS,
        num_months_data=NUM_MONTHS_HISTORICAL_TRAINING_DATA
    )

    training_df = data_loader.get_historical_data_df()

    data_transformer = DataSplitter()

    X_train, X_test, y_train, y_test = data_transformer.get_train_test_data(
        df=training_df,
        target_column=COLUMN_TO_PREDICT,
        test_size=TEST_SIZE
    )

    return X_train, X_test, y_train, y_test


def test_model_normalised_rmse(data_splits):
    X_train, X_test, y_train, y_test = data_splits

    model = DemandModel(random_state=RANDOM_STATE)

    assert model.score(
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test
    ) < 0.15
