import sys
import yaml
import pandas as pd
import mlflow
from typing import Dict, Any
import warnings
from sklearn.exceptions import DataConversionWarning
from src.constants import FEATURES_FILE_PATH, MODELS_FILE_PATH
from src.logging.logger import logging
from src.exception.exception import CustomException
from src.utils.telemetry_state import TelemetryState
from src.utils.mlfow_setup import setup_mlflow
warnings.filterwarnings(
    "ignore",
    message="X does not have valid feature names",
)

class TelemetryInferenceEngine:
    def __init__(self):
        try:
            logging.info("Initializing Telemetry Inference Engine")

            # ---------- DAGSHUB / MLFLOW SETUP ----------
            setup_mlflow(experiment_name=None)

            # ---------- Load configs ----------
            with open(FEATURES_FILE_PATH) as f:
                self.features_cfg = yaml.safe_load(f)

            with open(MODELS_FILE_PATH) as f:
                self.models_cfg = yaml.safe_load(f)["models"]

            # ---------- Load models (FAST) ----------
            self.models = {}
            for model_key in self.models_cfg:
                model_uri = self._registry_uri(model_key)
                logging.info(f"Loading model from MLflow Registry: {model_uri}")

                if model_key == "lap_time_regressor":
                    # XGBoost regressor
                    self.models[model_key] = mlflow.xgboost.load_model(model_uri)

                elif model_key == "gear_classifier":
                    # sklearn classifier
                    self.models[model_key] = mlflow.sklearn.load_model(model_uri)

                else:
                    # clustering → keep pyfunc
                    self.models[model_key] = mlflow.pyfunc.load_model(model_uri)

            self.state = TelemetryState()
            logging.info("Telemetry Inference Engine initialized successfully")

        except Exception as e:
            logging.exception("Failed to initialize inference engine")
            raise CustomException(e, sys)

    def process_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Sequentially replay telemetry CSV (streaming-style).
        """
        try:
            df = pd.read_csv(csv_path)
            outputs = []

            for i, row in df.iterrows():
                result = self.process_row(row)
                outputs.append(result)

                # 🔥 LOG EVERY 500 ROWS ONLY
                if i % 500 == 0:
                    logging.info(
                        f"Row {i} | lap={result['lap_number']} | "
                        f"pred_gear={result.get('predicted_gear')} | "
                        f"pred_lap_time={result.get('predicted_lap_time'):.2f}"
                    )

            logging.info("Streaming inference completed successfully")
            return pd.DataFrame(outputs)

        except Exception as e:
            logging.exception("CSV inference failed")
            raise CustomException(e, sys)

    def process_row(self, row: pd.Series) -> Dict[str, Any]:
        """
        Process one telemetry tick (FAST per-row inference).
        """
        try:
            output = {
                "lap_number": row.get("lap_number"),
                "race_position": row.get("race_position"),

                # ---------- TRUE LABELS ----------
                "true_lap_time": row.get("current_lap_time"),
                "true_gear": row.get("gear"),

                # Placeholder (clustering disabled)
                "driving_behavior": None,
            }

            # ================= REGRESSION =================
            if "lap_time_regressor" in self.models:
                feats = self.features_cfg["lap_time_regressor"]["features"]

                # 🔥 FAST: NumPy instead of DataFrame
                X_reg = row[feats].values.reshape(1, -1)

                output["predicted_lap_time"] = float(
                    self.models["lap_time_regressor"].predict(X_reg)[0]
                )

            # ================= CLASSIFICATION =================
            if "gear_classifier" in self.models:
                feats = self.features_cfg["gear_classifier"]["features"]

                # 🔥 FAST: NumPy instead of DataFrame
                X_clf = row[feats].values.reshape(1, -1)

                output["predicted_gear"] = int(
                    self.models["gear_classifier"].predict(X_clf)[0]
                )

            # ================= CLUSTERING =================
            # ❗ intentionally untouched & commented
            # completed_lap = self.state.update(row)
            #
            # if completed_lap is not None:
            #     agg_map = self.features_cfg["driving_behavior"]["aggregation"]
            #
            #     agg_df = completed_lap.agg(agg_map)
            #
            #     feature_row = {}
            #     for feature, stats in agg_map.items():
            #         for stat in stats:
            #             col_name = f"{feature}_{stat}"
            #             feature_row[col_name] = agg_df.loc[stat, feature]
            #
            #     lap_features = pd.DataFrame([feature_row])
            #
            #     if lap_features.isna().any().any():
            #         lap_features = lap_features.fillna(0.0)
            #
            #     label = self.models["driving_behavior"].predict(lap_features)[0]
            #
            #     output["driving_behavior"] = (
            #         "Aggressive Driving" if label == 1 else "Smooth Driving"
            #     )

            return output

        except Exception as e:
            logging.exception("Row inference failed")
            raise CustomException(e, sys)

    # ================= HELPERS =================
    @staticmethod
    def _registry_uri(model_key: str) -> str:
        """
        Resolve correct MLflow registry URI per model type.
        """
        return {
            "lap_time_regressor": "models:/LapTimeRegressor/Production",
            "gear_classifier": "models:/GearClassifier/Production",
            "driving_behavior": "models:/DrivingBehaviorCluster/latest",
        }[model_key]
