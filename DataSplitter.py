import pandas as pd


class DataSplitter:
    def __init__(
            self):
        pass

    def get_X_and_y_from_df(
        self,
        df,
        target_column
    ):
        if 'datetime' in df.columns:
            df.drop(labels=['datetime'], axis=1, inplace=True)

        X_cols = [col for col in df.columns if col != target_column]
        X = df[X_cols].to_numpy()

        y = df[target_column].to_numpy()

        return X, y

    def get_train_test_df(
        self,
        df,
        test_size
    ):
        df['datetime'] = pd.to_datetime(
            df[['year', 'month', 'day', 'hour']]
        )

        days_of_data = df['datetime'].max() - df['datetime'].min()
        test_threshold = df['datetime'].max() - days_of_data * test_size

        df_train = df[df['datetime'] <= test_threshold].copy()
        df_test = df[df['datetime'] > test_threshold].copy()

        return df_train, df_test

    def get_train_test_data(
        self,
        df,
        target_column,
        test_size
    ):
        df_train, df_test = self.get_train_test_df(
            df=df,
            test_size=test_size
        )

        X_train, y_train = self.get_X_and_y_from_df(
            df=df_train,
            target_column=target_column
        )

        X_test, y_test = self.get_X_and_y_from_df(
            df=df_test,
            target_column=target_column
        )

        return X_train, X_test, y_train, y_test
