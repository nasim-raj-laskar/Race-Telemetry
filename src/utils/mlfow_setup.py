import dagshub
import mlflow
from src.logging.logger import logging


def setup_mlflow():
    logging.info("Initializing DAGsHub MLflow")

    dagshub.init(
        repo_owner="nasim-raj-laskar",
        repo_name="race-telemetry",
        mlflow=True
    )

    tracking_uri = mlflow.get_tracking_uri()
    logging.info(f"MLflow tracking URI: {tracking_uri}")

    mlflow.set_experiment("Race-Telemetry-Evaluation")
