from DemandDataLoader import DemandDataLoader
import pytest


@pytest.fixture
def demand_data_loader():
    return DemandDataLoader()


def test_demand_data_loader_for_2026(demand_data_loader):
    df = demand_data_loader.get_historical_demand_data_df(years=['2026'])

    assert df.shape != (0, 0)

    print(df.columns)
    print(df)
