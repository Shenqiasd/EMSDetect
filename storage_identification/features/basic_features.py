from __future__ import annotations

import numpy as np
import pandas as pd


def compute_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    curve_cols = [col for col in result.columns if col.startswith("D") and col[1:].isdigit()]
    values = result[curve_cols].to_numpy(dtype=float)
    diffs = np.diff(values, axis=1)

    result["daily_max"] = values.max(axis=1)
    result["daily_min"] = values.min(axis=1)
    result["daily_mean"] = values.mean(axis=1)
    result["daily_std"] = values.std(axis=1)
    result["peak_valley_diff"] = result["daily_max"] - result["daily_min"]
    result["peak_valley_ratio"] = np.where(
        result["daily_min"] > 0, result["daily_max"] / result["daily_min"], np.nan
    )
    result["max_time_index"] = values.argmax(axis=1) + 1
    result["min_time_index"] = values.argmin(axis=1) + 1
    result["day_load_factor"] = np.where(
        result["daily_max"] > 0, result["daily_mean"] / result["daily_max"], np.nan
    )
    result["ramp_up_count"] = (diffs > 0).sum(axis=1)
    result["ramp_down_count"] = (diffs < 0).sum(axis=1)
    result["flat_segment_count"] = (np.abs(diffs) <= 0.5).sum(axis=1)
    return result
