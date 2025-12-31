import pandas as pd


class TelemetryState:
    def __init__(self):
        self.current_lap = None
        self.lap_buffer = []

    def update(self, row: pd.Series):
        lap_number = row["lap_number"]

        if self.current_lap is None:
            self.current_lap = lap_number

        # Lap changed → flush buffer
        if lap_number != self.current_lap:
            # Convert list of Series to DataFrame properly
            if self.lap_buffer:
                completed_lap = pd.DataFrame([s.to_dict() for s in self.lap_buffer])
            else:
                completed_lap = pd.DataFrame()
            self.lap_buffer = []
            self.current_lap = lap_number
            return completed_lap

        self.lap_buffer.append(row)
        return None