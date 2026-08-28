import pandas as pd
from config import BUCKET_NAME, PARQUET_FILE_NAME
import io
from google.cloud import storage


class CloudStorage:
    def __init__(
        self,
    ):
        self.client = storage.Client()

    def save_data(self, df):
        buffer = io.BytesIO()
        df.to_parquet(buffer)

        bucket = self.client.bucket(BUCKET_NAME)
        blob = bucket.blob(PARQUET_FILE_NAME)

        blob.upload_from_string(buffer.getvalue())

    def load_data(self):
        bucket = self.client.bucket(BUCKET_NAME)
        blob = bucket.blob(PARQUET_FILE_NAME)

        parquet_bytes = blob.download_as_bytes()
        df = pd.read_parquet(io.BytesIO(parquet_bytes))

        return df
