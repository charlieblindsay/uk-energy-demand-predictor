from datetime import datetime, timedelta
import streamlit as st
from google.cloud import storage
from config import BUCKET_NAME
import io
import pandas as pd


def main():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob('predictions.parquet')

    parquet_bytes = blob.download_as_bytes()
    df = pd.read_parquet(io.BytesIO(parquet_bytes))

    start_date = st.date_input(
        label='start_date',
        min_value=datetime.now(),
        max_value=datetime.now() + timedelta(days=217)
    )
    end_date = st.date_input(
        label='end_date',
        min_value=datetime.now(),
        max_value=datetime.now() + timedelta(days=217)
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
