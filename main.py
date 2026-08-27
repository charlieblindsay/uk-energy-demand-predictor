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

    df_filtered = df.loc[start_date:end_date + timedelta(days=1)]

    st.line_chart(df_filtered)


if __name__ == '__main__':
    main()
