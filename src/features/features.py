import numpy as np
import pandas as pd

def engineer_telemetry_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.fillna(0)

    # Remove invalid targets
    df = df[df["current_lap_time"] > 0]

    # Wheel slip magnitude
    df["wheel_slip_magnitude_front"] = np.sqrt(
        df["tire_slip_rotation_front_left"]**2 +
        df["tire_slip_rotation_front_right"]**2
    )

    df["wheel_slip_magnitude_rear"] = np.sqrt(
        df["tire_slip_rotation_rear_left"]**2 +
        df["tire_slip_rotation_rear_right"]**2
    )

    # Tire stress
    df["tire_stress_front"] = (
        df["tire_combined_slip_front_left"] +
        df["tire_combined_slip_front_right"]
    ) / 2

    df["tire_stress_rear"] = (
        df["tire_combined_slip_rear_left"] +
        df["tire_combined_slip_rear_right"]
    ) / 2

    # Avg tire temp
    df["avg_tire_temp"] = (
        df["tire_temp_front_left"] +
        df["tire_temp_front_right"] +
        df["tire_temp_rear_left"] +
        df["tire_temp_rear_right"]
    ) / 4

    # Acc & velocity magnitude
    df["acceleration_magnitude"] = np.sqrt(
        df["acceleration_x"]**2 +
        df["acceleration_y"]**2 +
        df["acceleration_z"]**2
    )

    df["velocity_magnitude"] = np.sqrt(
        df["velocity_x"]**2 +
        df["velocity_y"]**2 +
        df["velocity_z"]**2
    )

    # Steering rate
    df["steering_rate"] = df["steer"].diff().fillna(0)

    # RPM-speed ratio
    df["rpm_speed_ratio"] = df["current_engine_rpm"] / (df["speed"] + 1)

    return df