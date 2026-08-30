import pytest
from CloudStorage import CloudStorage
import numpy as np
import pandas as pd


@pytest.fixture
def df_stored_in_cloud():
    return CloudStorage().load_data()


def test_columns_in_loaded_df(df_stored_in_cloud):
    assert df_stored_in_cloud.columns.tolist() == ['demand', 'predicted']


def test_data_types_of_df(df_stored_in_cloud):
    assert isinstance(df_stored_in_cloud.index, pd.DatetimeIndex)
    assert isinstance(df_stored_in_cloud.iloc[0]['demand'], float)
    assert isinstance(df_stored_in_cloud.iloc[0]['predicted'], (bool, np.bool_))
