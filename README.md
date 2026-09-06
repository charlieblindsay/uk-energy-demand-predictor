# uk-energy-demand-predictor

A pipeline that forecasts UK national electricity demand from weather data, and a [Streamlit](https://streamlit.io/) app for viewing actual vs. predicted demand. It runs on Google Cloud: a scheduled Cloud Run **job** retrains the model on fresh data, and a Cloud Run **service** serves the Streamlit dashboard.

## What it does

1. **Pulls historical UK electricity demand** from [NESO](https://www.neso.energy/) (National Energy System Operator) demand data CSVs, for a configurable trailing window (`NUM_MONTHS_HISTORICAL_TRAINING_DATA` in `config.py`, currently 12 months). Demand values are half-hourly settlement periods, resampled to hourly.
2. **Pulls historical and forecast weather data** for 8 UK cities (London, Birmingham, Manchester, Leeds, Bristol, Cardiff, Glasgow, Edinburgh) from the [Open-Meteo](https://open-meteo.com/) historical-forecast and seasonal-forecast APIs — temperature, relative humidity, and apparent temperature — plus derived UK public-holiday and day-of-week flags.
3. **Merges weather and demand data** on year/month/day/hour and trains a `sklearn.tree.DecisionTreeRegressor` to predict national demand (`ND`) from the weather/calendar features.
4. **Generates a forecast** for the next `NUM_DAYS_OF_FORECASTING` days (currently 217) using forecast weather data, and writes historical + predicted demand to a Parquet file in Google Cloud Storage.
5. **Serves a Streamlit dashboard** that loads that Parquet file and plots actual vs. predicted demand over a date range the user picks, along with the timestamp of the last retrain.

The model is a single decision tree with no hyperparameter tuning — it's a simple, interpretable baseline, not a tuned production forecaster.

## Repo structure

| File | Role |
|---|---|
| `main.py` | Streamlit app entrypoint — loads data from GCS, shows the last retrain time, renders the actual-vs-predicted chart |
| `update_data.py` | Retraining job entrypoint — loads data, trains the model, generates forecasts, writes results to GCS |
| `DataLoader.py` | Combines weather + demand data into a training set, and builds the weather-only input set used for forecasting |
| `DemandDataLoader.py` | Downloads and parses NESO historical demand CSVs |
| `WeatherDataLoader.py` | Fetches historical/forecast weather from Open-Meteo, adds holiday and day-of-week features |
| `DemandDataFrameBuilder.py` | Combines historical demand with future predictions into one time-indexed dataframe, flagged `predicted`/not |
| `DataSplitter.py` | Splits into train/test **chronologically** (not shuffled) — the most recent `test_size` fraction of the date range is held out |
| `DemandModel.py` | Thin wrapper around `DecisionTreeRegressor`; `score()` returns RMSE normalized by mean demand |
| `CloudStorage.py` | Reads/writes the demand+prediction dataframe as a Parquet file in a GCS bucket |
| `JobExecutionViewer.py` | Looks up the last successful execution time of the Cloud Run retraining job, shown in the app |
| `DemandDataViewer.py` | Helpers for filtering the combined dataframe into actual vs. predicted series for charting |
| `config.py` | All configuration: GCS bucket/file names, region, weather locations/metrics, training window, forecast horizon, test split, random seed |
| `Dockerfile` | Builds the Streamlit service container |
| `Dockerfile.job` | Builds the retraining job container |
| `cloudbuild.yaml` | Cloud Build pipeline: builds and pushes both containers, deploys the Cloud Run service, and updates the Cloud Run job |
| `test_*.py` | Unit tests for the loaders, splitter, model, and cloud storage wrapper |

## Data sources

- **Demand**: [NESO Data Portal](https://www.neso.energy/data-portal) — half-hourly national electricity demand (`ND` column), aggregated to hourly by taking even settlement periods.
- **Weather**: [Open-Meteo](https://open-meteo.com/) — `historical-forecast-api` for past data (UKMO Seamless model) and `seasonal-api` for the forecast window.
- **Holidays**: the [`holidays`](https://pypi.org/project/holidays/) Python package, UK calendar.

## Running locally

```bash
pip install -r requirements.txt
```

**Retrain the model and refresh the stored data:**
```bash
python update_data.py
```
This requires Google Cloud credentials with access to the `BUCKET_NAME` set in `config.py` (Application Default Credentials, e.g. via `gcloud auth application-default login`).

**Run the dashboard:**
```bash
streamlit run main.py
```

**Run the tests:**
```bash
pytest
```

## Deployment

`cloudbuild.yaml` defines two build/deploy steps against Google Cloud:

- **`update-container`** — the Streamlit dashboard, deployed as a Cloud Run **service** (`Dockerfile`).
- **`update-demand-data`** — the retraining pipeline, deployed as a Cloud Run **job** (`Dockerfile.job`), intended to be run on a schedule (e.g. via Cloud Scheduler) to keep the model and forecasts current.

Both push images to Artifact Registry in `europe-west1` and are wired up via `create-trigger.json` / a Cloud Build trigger for CI-style deploys on push.

## Configuration

All tunable parameters live in `config.py`:

| Variable | Purpose |
|---|---|
| `BUCKET_NAME`, `PARQUET_FILE_NAME` | Where the combined actual/predicted dataframe is stored in GCS |
| `RANDOM_STATE` | Seed for the decision tree |
| `REGION`, `DATA_JOB_NAME` | Used to look up the Cloud Run job's last execution time |
| `NUM_MONTHS_HISTORICAL_TRAINING_DATA` | How much history to train on |
| `COLUMN_TO_PREDICT` | Target column (`ND`) |
| `TEST_SIZE` | Fraction of the date range held out for chronological testing |
| `NUM_DAYS_OF_FORECASTING` | How far ahead to forecast |
| `UK_WEATHER_LOCATIONS` | The 8 cities and their coordinates used as weather features |
| `WEATHER_METRICS` | Which Open-Meteo hourly variables to pull |

## Notes / caveats

- There's no notion of model versioning, evaluation dashboarding, or hyperparameter search here — `DemandModel.score()` exists but isn't wired into `update_data.py`'s retraining flow, so each run simply refits on the latest data and overwrites the previous predictions.
- The `.cache.sqlite` file in the repo root is the `requests-cache` HTTP cache used by the Open-Meteo client during local runs.
