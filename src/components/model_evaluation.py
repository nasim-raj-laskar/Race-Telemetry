import json
import joblib
import pandas as pd
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import sys
from sklearn.pipeline import Pipeline
from mlflow.tracking import MlflowClient
from src.evaluators.evaluation import (evaluate_regression,evaluate_classification,evaluate_clustering)
from src.evaluators.visualization import (plot_regression_actual_vs_pred,plot_confusion_matrix,plot_clustering_pca)
from src.logging.logger import logging
from src.exception.exception import CustomException


class ModelEvaluation:
    def __init__(self, config, features_cfg):
        self.config = config
        self.features = features_cfg

    def evaluate(self):
        try:
            logging.info("Starting model evaluation")
            val = pd.read_csv(self.config.val_path)
            metrics = {}

            with mlflow.start_run(run_name="model_evaluation") as run:
                logging.info(f"MLflow run_id: {run.info.run_id}")

                # ================= REGRESSION =================
                logging.info("Evaluating lap_time_regressor")

                reg_model = joblib.load(
                    self.config.model_paths["lap_time_regressor"]
                )
                reg_feats = self.features["lap_time_regressor"]["features"]

                X_val = val[reg_feats]
                y_val = val["current_lap_time"]
                y_pred = reg_model.predict(X_val)

                reg_metrics = evaluate_regression(y_val, y_pred)
                metrics["lap_time_regressor"] = reg_metrics
                mlflow.log_metrics({f"reg_{k}": v for k, v in reg_metrics.items()})

                mlflow.xgboost.log_model(reg_model,artifact_path="models/lap_time_regressor",registered_model_name="LapTimeRegressor")

                reg_plot = self.config.root_dir / "regression_actual_vs_pred.png"
                plot_regression_actual_vs_pred(y_val, y_pred, reg_plot)
                mlflow.log_artifact(str(reg_plot))

                # ================= CLASSIFICATION =================
                logging.info("Evaluating gear_classifier")

                cls_model = joblib.load(
                    self.config.model_paths["gear_classifier"]
                )
                cls_feats = self.features["gear_classifier"]["features"]

                X_val = val[cls_feats]
                y_val = val["gear"]
                y_pred = cls_model.predict(X_val)

                cls_metrics = evaluate_classification(y_val, y_pred)
                metrics["gear_classifier"] = cls_metrics
                mlflow.log_metrics({f"cls_{k}": v for k, v in cls_metrics.items()})

                mlflow.sklearn.log_model(
                    cls_model,
                    artifact_path="models/gear_classifier",
                    registered_model_name="GearClassifier"
                )

                cm_path = self.config.root_dir / "gear_confusion_matrix.png"
                plot_confusion_matrix(y_val, y_pred, cm_path)
                mlflow.log_artifact(str(cm_path))

                # ================= CLUSTERING =================
                logging.info("Evaluating driving_behavior clustering")

                kmeans = joblib.load(
                    self.config.model_paths["driving_behavior"]
                )
                scaler = joblib.load(
                    self.config.scaler_paths["driving_behavior"]
                )

                agg_map = self.features["driving_behavior"]["aggregation"]
                lap_features = val.groupby("lap_number").agg(agg_map)
                lap_features.columns = ["_".join(col) for col in lap_features.columns]

                X_scaled = scaler.transform(lap_features)
                labels = kmeans.predict(X_scaled)

                cluster_metrics = evaluate_clustering(X_scaled, labels)
                metrics["driving_behavior"] = cluster_metrics
                mlflow.log_metrics(
                    {f"cluster_{k}": v for k, v in cluster_metrics.items()}
                )

                cluster_pipeline = Pipeline(
                    steps=[("scaler", scaler), ("kmeans", kmeans)]
                )

                mlflow.sklearn.log_model(
                    cluster_pipeline,
                    artifact_path="models/driving_behavior",
                    registered_model_name="DrivingBehaviorCluster"
                )

                pca_path = self.config.root_dir / "driving_behavior_pca.png"
                plot_clustering_pca(X_scaled, labels, pca_path)
                mlflow.log_artifact(str(pca_path))

                # ================= SAVE METRICS =================
                with open(self.config.metrics_path, "w") as f:
                    json.dump(metrics, f, indent=4)

                mlflow.log_artifact(str(self.config.metrics_path))

                # ================= AUTO PROMOTION =================
                client = MlflowClient()

                if reg_metrics["r2"] > 0.95:
                    version = client.get_latest_versions(
                        "LapTimeRegressor", stages=["None"]
                    )[0].version
                    client.transition_model_version_stage(
                        "LapTimeRegressor", version, "Production", True
                    )
                    logging.info("LapTimeRegressor promoted to Production")

                if cls_metrics["accuracy"] > 0.94:
                    version = client.get_latest_versions(
                        "GearClassifier", stages=["None"]
                    )[0].version
                    client.transition_model_version_stage(
                        "GearClassifier", version, "Production", True
                    )
                    logging.info("GearClassifier promoted to Production")

            logging.info("Model evaluation completed successfully")
            return metrics

        except Exception as e:
            logging.exception("Model evaluation failed")
            raise CustomException(e, sys)