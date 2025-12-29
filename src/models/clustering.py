from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def train_clustering(X, params):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = KMeans(**params)
    model.fit(X_scaled)

    return model, scaler
