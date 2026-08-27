from datetime import timedelta
import streamlit as st
from google.cloud import storage
from config import BUCKET_NAME
import io
import pandas as pd

from google.cloud import run_v2
import google.auth


def main():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob('predictions.parquet')

    parquet_bytes = blob.download_as_bytes()
    df = pd.read_parquet(io.BytesIO(parquet_bytes))

    min_historical_date = df[~df['predicted']].index.min().date()
    max_historical_date = df[~df['predicted']].index.max().date()

    st.write(f'Training data range: {min_historical_date} - {max_historical_date}')
    _, project_id = google.auth.default()

    REGION = "europe-west1"
    JOB_NAME = "update-demand-data"

    client = run_v2.ExecutionsClient()

    parent = (
        f"projects/{project_id}"
        f"/locations/{REGION}"
        f"/jobs/{JOB_NAME}"
    )

    executions = client.list_executions(parent=parent)

    latest_execution = next(iter(executions), None)

    if latest_execution:
        st.write("Last time data was refreshed and model was retrained on new data:", latest_execution.completion_time)

    min_date = df.index.min().date()
    max_date = df.index.max().date()

    start_date = st.date_input(
        label='start_date',
        min_value=min_date,
        max_value=max_date
    )
    end_date = st.date_input(
        label='end_date',
        min_value=min_date,
        max_value=max_date
    )

    df_filtered = df.loc[
        pd.Timestamp(start_date):
        pd.Timestamp(end_date) + timedelta(days=1)
    ].copy()

    today = pd.Timestamp.today().normalize()

    df_filtered['Actual'] = df_filtered.iloc[:, 0].where(
        df_filtered.index <= today
    )

    df_filtered['Predicted'] = df_filtered.iloc[:, 0].where(
        df_filtered.index > today
    )

    st.line_chart(
        df_filtered[["Actual", "Predicted"]],
        color=["#0000FF", "#00AA00"]
    )


if __name__ == '__main__':
    main()
