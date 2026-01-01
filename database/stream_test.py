import time
import pandas as pd
from src.pipeline.inferencing_pipeline import TelemetryInferenceEngine

def simulated_db_stream(csv_path, delay=8.5):
    df = pd.read_csv(csv_path)

    for _, row in df.iterrows():
        yield row
        time.sleep(delay)  # simulate remote DB latency

engine = TelemetryInferenceEngine()

for row in simulated_db_stream( 
    "artifacts/data_transformation/val.csv",
    delay=0.25
):
    result = engine.process_row(row)

    print(
        f"[LIVE] lap={result['lap_number']} | "
        f"true_gear={result['true_gear']} → pred_gear={result['predicted_gear']} | "
        f"true_time={result['true_lap_time']:.2f} → pred_time={result['predicted_lap_time']:.2f} | "
        f"behavior={result.get('driving_behavior')}"
    )

