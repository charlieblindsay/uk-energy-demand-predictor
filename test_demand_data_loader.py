from DemandDataLoader import DemandDataLoader
import pytest


@pytest.fixture
def demand_data_loader():
    return DemandDataLoader()


def test_demand_data_loader_for_2026(demand_data_loader):
    df = demand_data_loader.get_historical_demand_data_df(years=['2026'])

    assert df.shape != (0, 0)
    assert 2026 in df['year'].unique()


def test_demand_data_loader_for_2025(demand_data_loader):
    df = demand_data_loader.get_historical_demand_data_df(years=['2025'])

    assert df.shape != (0, 0)
    assert 2025 in df['year'].unique()
    assert set(df['month'].unique()) == set(range(1, 13))


def test_demand_data_loader_for_2024(demand_data_loader):
    df = demand_data_loader.get_historical_demand_data_df(years=['2024'])

    assert df.shape != (0, 0)
    assert 2024 in df['year'].unique()
    assert set(df['month'].unique()) == set(range(1, 13))


def test_demand_data_loader_for_multiple_years(demand_data_loader):
    df = demand_data_loader.get_historical_demand_data_df(years=['2024', '2025', '2026'])

    assert df.shape != (0, 0)
    assert 2024 in df['year'].unique()
    assert 2025 in df['year'].unique()
    assert 2026 in df['year'].unique()
