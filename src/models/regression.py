from xgboost import XGBRegressor


def train_regressor(X, y, params):
    model = XGBRegressor(**params)
    model.fit(X, y)
    return model