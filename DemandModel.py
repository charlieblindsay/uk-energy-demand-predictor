from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import root_mean_squared_error


class DemandModel:
    def __init__(self, random_state):
        self._model = DecisionTreeRegressor(random_state=random_state)

    def fit(self, X_train, y_train):
        self._model.fit(X_train, y_train)

    def predict(self, X):
        return self._model.predict(X)

    def score(self, X_train, y_train, X_test, y_test):
        self.fit(X_train, y_train)

        y_predict = self.predict(X_test)

        return root_mean_squared_error(
            y_true=y_test,
            y_pred=y_predict
        ) / y_test.mean()
