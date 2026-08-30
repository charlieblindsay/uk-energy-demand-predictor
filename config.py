BUCKET_NAME = 'uk-energy-demand-predictions'
PARQUET_FILE_NAME = "predictions.parquet"
RANDOM_STATE = 42
REGION = "europe-west1"
DATA_JOB_NAME = "update-demand-data"

NUM_MONTHS_HISTORICAL_TRAINING_DATA = 12
COLUMN_TO_PREDICT = 'ND'
TEST_SIZE = 0.2

NUM_DAYS_OF_FORECASTING = 217

UK_WEATHER_LOCATIONS = {
    "London": {
        "latitude": 51.5074,
        "longitude": -0.1278
    },
    "Birmingham": {
        "latitude": 52.4862,
        "longitude": -1.8904
    },
    "Manchester": {
        "latitude": 53.4808,
        "longitude": -2.2426
    },
    "Leeds": {
        "latitude": 53.8008,
        "longitude": -1.5491
    },
    "Bristol": {
        "latitude": 51.4545,
        "longitude": -2.5879
    },
    "Cardiff": {
        "latitude": 51.4816,
        "longitude": -3.1791
    },
    "Glasgow": {
        "latitude": 55.8642,
        "longitude": -4.2518
    },
    "Edinburgh": {
        "latitude": 55.9533,
        "longitude": -3.1883
    }
}
WEATHER_METRICS = [
    'temperature_2m',
    'relative_humidity_2m',
    'apparent_temperature'
]
