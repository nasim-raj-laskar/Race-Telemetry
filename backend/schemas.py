from pydantic import BaseModel
from typing import Optional

class InferenceResponse(BaseModel):
    # ---- Identity / Time surrogate ----
    id: int
    lap_number: float
    race_position: float

    # ---- Raw Telemetry ----
    speed: float
    current_engine_rpm: float
    avg_tire_temp: float
    tire_stress_front: float
    tire_stress_rear: float
    wheel_slip_magnitude_front: float
    wheel_slip_magnitude_rear: float

    power : float
    torque: float
    boost: float
    pitch : float
    roll : float
    
    yaw: float
    steer: float
    gear: int


    # ---- ML Outputs ----
    predicted_lap_time: float
    predicted_gear: int
    driving_behavior: Optional[str]
