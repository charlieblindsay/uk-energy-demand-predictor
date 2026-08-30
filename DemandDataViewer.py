import pandas as pd
from datetime import timedelta


class DemandDataViewer:
    def __init__(self, df):
        self._df = df

    @property
    def min_historical_date(self):
        return self._df[~self._df['predicted']].index.min().date()

    @property
    def max_historical_date(self):
        return self._df[~self._df['predicted']].index.max().date()

    @property
    def min_date(self):
        return self._df.index.min().date()

    @property
    def max_date(self):
        return self._df.index.max().date()

    def get_df_actual_filtered_vs_predicted(self, start_date, end_date):
        df_filtered = self._df.loc[
            pd.Timestamp(start_date): pd.Timestamp(end_date) + timedelta(days=1)
        ].copy()

        df_filtered['Actual'] = df_filtered['demand'].where(
            ~df_filtered['predicted']
        )
        df_filtered['Predicted'] = df_filtered['demand'].where(
            df_filtered['predicted']
        )

        return df_filtered[['Actual', 'Predicted']]
