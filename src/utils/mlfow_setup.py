import dagshub
import mlflow
from src.logging.logger import logging


def setup_mlflow(experiment_name: str | None = None):
    logging.info("Initializing DAGsHub MLflow")

    dagshub.init(
        repo_owner="nasim-raj-laskar",
        repo_name="race-telemetry",
        mlflow=True
    )

    if experiment_name:
        mlflow.set_experiment(experiment_name)

    logging.info(f"MLflow tracking URI: {mlflow.get_tracking_uri()}")
    logging.info("DAGsHub MLflow initialized successfully")
