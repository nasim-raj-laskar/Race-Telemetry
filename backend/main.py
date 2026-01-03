from fastapi import FastAPI
from backend.database import SessionLocal
from backend.crud import fetch_rows_after_id
from backend.schemas import InferenceResponse
from src.pipeline.inferencing_pipeline import TelemetryInferenceEngine
import pandas as pd

app = FastAPI(title="Race Telemetry Inference API")

engine = TelemetryInferenceEngine()

LAST_ID = 0   # cursor (later: Redis / DB)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "race-telemetry-backend"
    }

@app.get("/infer/next", response_model=list[InferenceResponse])
def infer_next(batch_size: int = 1):
    global LAST_ID

    db = SessionLocal()
    try:
        rows = fetch_rows_after_id(db, LAST_ID, batch_size)

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

                "power" : row["power"],
                "torque": row["torque"],
                "boost": row["boost"],
                "pitch" : row["pitch"],
                "roll" : row["roll"],

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
        db.close()
