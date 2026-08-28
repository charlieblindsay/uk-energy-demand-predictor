import pytest
from CloudStorage import CloudStorage


def test_columns_in_loaded_df():
    df = CloudStorage().load_data()
    print(df.columns.tolist())
    print(df.head())
