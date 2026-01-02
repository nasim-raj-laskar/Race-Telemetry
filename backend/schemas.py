from pydantic import BaseModel
from typing import Optional

class InferenceResponse(BaseModel):
    id: int
    lap_number: float
    race_position: float
    predicted_lap_time: float
    predicted_gear: int
    driving_behavior: Optional[str]
