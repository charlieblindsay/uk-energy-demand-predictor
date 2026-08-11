import pytest
from WeatherDataLoader import WeatherDataLoader

@pytest.fixture
def weather_data_loader():
    return WeatherDataLoader(
        weather_locations_dict={
            "London": {
                "latitude": 51.5074,
                "longitude": -0.1278
            }
        },
        metrics=[
            'temperature_2m'
        ],
    )


def test_if_api_can_produce_historical_weather(weather_data_loader):
    df = weather_data_loader.get_historical_weather_data_df(
        start_date='2026-01-01',
        end_date='2026-08-01'
    )

    assert df[df['month'] == 7].shape[0] != 0
    assert df[df['month'] == 9].shape[0] == 0

    print(df.columns)


def test_if_api_can_produce_forecasted_weather(weather_data_loader):
    df = weather_data_loader.get_forecast_weather_data_df(
        num_days_to_forecast=217
    )

    assert df[df['month'] == 7].shape[0] == 0
    assert df[df['month'] == 9].shape[0] != 0

    print(df.columns)
