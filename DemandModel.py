from sklearn.tree import DecisionTreeRegressor


class DemandModel:
    def __init__(self, random_state):
        self._model = DecisionTreeRegressor(random_state=random_state)

    def fit(self, X_train, y_train):
        self._model.fit(X_train, y_train)

    def predict(self, X):
        return self._model.predict(X)
