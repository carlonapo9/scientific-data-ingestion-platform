import pandas as pd
import numpy as np

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Input format:
    sample_id | timestamp | sensor_index | value
    """

    df = df.copy()

    # sort properly
    df = df.sort_values(["sample_id", "sensor_index", "timestamp"])

    # rolling stats per engine + sensor
    df["rolling_mean"] = df.groupby(
        ["sample_id", "sensor_index"]
    )["value"].transform(lambda x: x.rolling(5, min_periods=1).mean())

    df["rolling_std"] = df.groupby(
        ["sample_id", "sensor_index"]
    )["value"].transform(lambda x: x.rolling(5, min_periods=1).std().fillna(0))

    # delta features
    df["diff"] = df.groupby(
        ["sample_id", "sensor_index"]
    )["value"].diff().fillna(0)

    return df