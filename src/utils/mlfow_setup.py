import os
import dagshub
import mlflow
from src.logging.logger import logging


def setup_mlflow(experiment_name=None):
    try:
        token = os.getenv("DAGSHUB_USER_TOKEN")
        if not token:
            raise RuntimeError("DAGSHUB_USER_TOKEN not set")

        os.environ["DAGSHUB_USER_TOKEN"] = token

        dagshub.init(
            repo_owner="nasim-raj-laskar",
            repo_name="race-telemetry",
            mlflow=True
        )

        if experiment_name:
            mlflow.set_experiment(experiment_name)

        logging.info("DAGsHub MLflow initialized successfully")

    except Exception as e:
        logging.warning(
            f"DAGsHub MLflow initialization skipped: {e}"
        )
