import pandas as pd
from sklearn.model_selection import train_test_split


class DataTransformer:
    def __init__(
            self):
        pass

    def get_train_test_split(self, df, target_column, test_size):
        y = df[target_column].to_numpy()

        X_cols = [col for col in df.columns if col != target_column]
        X = df[X_cols].to_numpy()

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size
        )

        return X_train, X_test, y_train, y_test
