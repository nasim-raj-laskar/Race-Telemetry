import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.decomposition import PCA


# ---------- Regression ----------
def plot_regression_actual_vs_pred(y_true, y_pred, save_path):
    plt.figure(figsize=(6, 6))
    plt.scatter(y_true, y_pred, alpha=0.4)
    plt.plot([y_true.min(), y_true.max()],
             [y_true.min(), y_true.max()], "r--")
    plt.xlabel("Actual")
    plt.ylabel("Predicted")
    plt.title("Actual vs Predicted (Regression)")
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()


# ---------- Classification ----------
def plot_confusion_matrix(y_true, y_pred, save_path):
    cm = confusion_matrix(y_true, y_pred, normalize="true")
    disp = ConfusionMatrixDisplay(cm)
    disp.plot(cmap="Blues", values_format=".2f")
    plt.title("Normalized Confusion Matrix")
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()


# ---------- Clustering ----------
def plot_clustering_pca(X_scaled, labels, save_path):
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    plt.figure(figsize=(6, 6))
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap="viridis", s=25)
    plt.title("Clustering PCA Projection")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()