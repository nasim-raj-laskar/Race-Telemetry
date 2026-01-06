from fastapi import FastAPI
from backend.database import SessionLocal
from backend.crud import fetch_rows_after_id
from backend.schemas import InferenceResponse
from backend.metrics import INFERENCE_LATENCY, REQUEST_COUNT,FEATURE_PSI
from backend.drift import compute_feature_drift
from src.pipeline.inferencing_pipeline import TelemetryInferenceEngine
from prometheus_client import make_asgi_app
import pandas as pd
import time
import os

TRAIN_DF = pd.read_csv("artifacts/data_transformation/val.csv")

DRIFT_FEATURES = [
    "speed",
    "current_engine_rpm",
    "boost",
    "torque",
    "avg_tire_temp"
]

app = FastAPI(title="Race Telemetry Inference API")

engine = TelemetryInferenceEngine()

LAST_ID = 0   # cursor 

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "race-telemetry-backend"
    }

import time

@app.get("/infer/next", response_model=list[InferenceResponse])
def infer_next(batch_size: int = 1):
    global LAST_ID

    start_time = time.time()
    REQUEST_COUNT.inc()

    db = SessionLocal()
    try:
        rows = fetch_rows_after_id(db, LAST_ID, batch_size)

        if not rows:
            return []

        prod_df = pd.DataFrame(rows)

        #simulate drift
        prod_df["current_engine_rpm"] *= 1.05
        prod_df["boost"] *= 1.08

        psi_results = compute_feature_drift(
            TRAIN_DF,
            prod_df,
            DRIFT_FEATURES
        )

        for feature, psi in psi_results.items():
            FEATURE_PSI.labels(feature=feature).set(psi)

        results = []
        for row in rows:
            LAST_ID = row["id"]

            series = pd.Series(row)
            prediction = engine.process_row(series)

            results.append({
                # Identity
                "id": row["id"],
                "lap_number": row["lap_number"],
                "race_position": row["race_position"],

                # Raw telemetry
                "speed": row["speed"],
                "current_engine_rpm": row["current_engine_rpm"],
                "avg_tire_temp": row["avg_tire_temp"],
                "tire_stress_front": row["tire_stress_front"],
                "tire_stress_rear": row["tire_stress_rear"],
                "wheel_slip_magnitude_front": row["wheel_slip_magnitude_front"],
                "wheel_slip_magnitude_rear": row["wheel_slip_magnitude_rear"],
                "power": row["power"],
                "torque": row["torque"],
                "boost": row["boost"],
                "pitch": row["pitch"],
                "roll": row["roll"],
                "yaw": row["yaw"],
                "steer": row["steer"],
                "gear": row["gear"],

                # ML outputs
                "predicted_lap_time": prediction["predicted_lap_time"],
                "predicted_gear": prediction["predicted_gear"],
                "driving_behavior": prediction["driving_behavior"],
            })

        return results

    finally:
        INFERENCE_LATENCY.observe(time.time() - start_time)
        db.close()

app.mount("/metrics", make_asgi_app())