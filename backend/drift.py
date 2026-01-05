import numpy as np

def compute_psi(expected, actual, bins=10):
    expected = np.asarray(expected)
    actual = np.asarray(actual)

    breakpoints = np.percentile(
        expected, np.linspace(0, 100, bins + 1)
    )

    e_hist, _ = np.histogram(expected, bins=breakpoints)
    a_hist, _ = np.histogram(actual, bins=breakpoints)

    e_pct = e_hist / len(expected)
    a_pct = a_hist / len(actual)

    psi = np.sum(
        (a_pct - e_pct) *
        np.log((a_pct + 1e-6) / (e_pct + 1e-6))
    )

    return float(psi)


def compute_feature_drift(train_df, prod_df, features):
    drift = {}
    for f in features:
        drift[f] = compute_psi(train_df[f], prod_df[f])
    return drift
