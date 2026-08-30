from DataLoader import DataLoader
from DataSplitter import DataSplitter
import pytest

from config import UK_WEATHER_LOCATIONS, WEATHER_METRICS
from config import NUM_MONTHS_HISTORICAL_TRAINING_DATA
from config import TEST_SIZE


@pytest.fixture
def train_test_dfs():
    data_loader = DataLoader(
        weather_data_locations=UK_WEATHER_LOCATIONS,
        weather_metrics=WEATHER_METRICS,
        num_months_data=NUM_MONTHS_HISTORICAL_TRAINING_DATA
    )

    training_df = data_loader.get_historical_data_df()

    data_transformer = DataSplitter()

    df_train, df_test = data_transformer.get_train_test_df(
        df=training_df,
        test_size=TEST_SIZE
    )

    return df_train, df_test


def test_train_dates_before_test_dates(train_test_dfs):
    df_train, df_test = train_test_dfs

    assert df_train['datetime'].max() < df_test['datetime'].min()


def test_train_and_test_dfs_are_right_size(train_test_dfs):
    df_train, df_test = train_test_dfs

    assert df_train.shape[0] >= 3.75 * df_test.shape[0]
