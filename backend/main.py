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
                "id": row["id"],
                "lap_number": prediction["lap_number"],
                "race_position": prediction["race_position"],
                "predicted_lap_time": prediction["predicted_lap_time"],
                "predicted_gear": prediction["predicted_gear"],
                "driving_behavior": prediction["driving_behavior"]
            })

        return results

    finally:
        db.close()
