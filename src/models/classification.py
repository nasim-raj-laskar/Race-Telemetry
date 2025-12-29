from sklearn.ensemble import RandomForestClassifier

def train_classifier(X, y, params):
    model = RandomForestClassifier(**params)
    model.fit(X, y)
    return model
