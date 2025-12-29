import pandas as pd
import joblib, os
from src.models.regression import train_regressor
from src.models.classification import train_classifier
from src.models.clustering import train_clustering
from src.models.evaluation import (evaluate_regression,evaluate_classification,evaluate_clustering)
from src.logging.logger import logging
from src.exception.exception import CustomException
from sklearn.metrics import classification_report


class ModelTrainer:
    def __init__(self, config, models_cfg, features_cfg, params_cfg):
        self.config = config
        self.models = models_cfg["models"]
        self.features = features_cfg
        self.params = params_cfg

    def initiate_model_training(self):
        try:
            train = pd.read_csv(self.config.train_path)
            val = pd.read_csv(self.config.val_path)

            for model_name, model_cfg in self.models.items():
                logging.info(f"========== Training model: {model_name} ==========")

                model_type = model_cfg["type"]
                target = model_cfg.get("target")

                model_dir = os.path.join(
                    self.config.model_root_dir,
                    model_cfg["artifact_dir"]
                )
                os.makedirs(model_dir, exist_ok=True)

                # ---------------- REGRESSION ----------------
                if model_type == "regression":
                    feats = self.features[model_name]["features"]

                    X_train, y_train = train[feats], train[target]
                    X_val, y_val = val[feats], val[target]

                    model = train_regressor(
                        X_train, y_train, self.params["regression"]
                    )

                    # Train metrics
                    y_train_pred = model.predict(X_train)
                    train_metrics = evaluate_regression(y_train, y_train_pred)

                    # Val metrics
                    y_val_pred = model.predict(X_val)
                    val_metrics = evaluate_regression(y_val, y_val_pred)

                    logging.info(f"Regression TRAIN metrics: {train_metrics}")
                    logging.info(f"Regression VAL   metrics: {val_metrics}")

                    joblib.dump(model, f"{model_dir}/model.pkl")

                # ---------------- CLASSIFICATION ----------------
                elif model_type == "classification":
                    feats = self.features[model_name]["features"]

                    X_train, y_train = train[feats], train[target]
                    X_val, y_val = val[feats], val[target]

                    model = train_classifier(
                        X_train, y_train, self.params["classification"]
                    )

                    # Train metrics
                    y_train_pred = model.predict(X_train)
                    train_metrics = evaluate_classification(y_train, y_train_pred)

                    # Val metrics
                    y_val_pred = model.predict(X_val)
                    val_metrics = evaluate_classification(y_val, y_val_pred)

                    logging.info(f"Classification TRAIN metrics: {train_metrics}")
                    logging.info(f"Classification VAL   metrics: {val_metrics}")

                    logging.info(
                        "Validation Classification Report:\n"
                        + classification_report(y_val, y_val_pred)
                    )

                    joblib.dump(model, f"{model_dir}/model.pkl")

                # ---------------- CLUSTERING ----------------
                elif model_type == "clustering":
                    agg_map = self.features[model_name]["aggregation"]

                    lap_features = train.groupby("lap_number").agg(agg_map)
                    lap_features.columns = [
                        "_".join(col) for col in lap_features.columns
                    ]

                    model, scaler = train_clustering(
                        lap_features, self.params["clustering"]
                    )

                    X_scaled = scaler.transform(lap_features)
                    labels = model.labels_

                    metrics = evaluate_clustering(X_scaled, labels)

                    logging.info(f"Clustering metrics: {metrics}")
                    logging.info(f"Inertia: {model.inertia_}")

                    joblib.dump(model, f"{model_dir}/model.pkl")
                    joblib.dump(scaler, f"{model_dir}/scaler.pkl")

                logging.info(f"Artifacts saved for {model_name}")

        except Exception as e:
            logging.error("Model training failed", exc_info=True)
            raise CustomException(e)
