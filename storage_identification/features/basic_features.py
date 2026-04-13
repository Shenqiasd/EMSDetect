from __future__ import annotations

import numpy as np
import pandas as pd


def compute_basic_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    curve_cols = [f"D{idx}" for idx in range(1, 97) if f"D{idx}" in result.columns]
    if not curve_cols:
        raise ValueError("No valid curve columns found. Expected D1..D96.")
    values = result[curve_cols].to_numpy(dtype=float)
    diffs = np.diff(values, axis=1)
    all_nan = np.isnan(values).all(axis=1)
    safe_values = values.copy()
    safe_values[all_nan] = 0.0

    result["daily_max"] = np.nanmax(safe_values, axis=1)
    result["daily_min"] = np.nanmin(safe_values, axis=1)
    result["daily_mean"] = np.nanmean(safe_values, axis=1)
    result["daily_std"] = np.nanstd(safe_values, axis=1)
    result["peak_valley_diff"] = result["daily_max"] - result["daily_min"]
    result["peak_valley_ratio"] = np.where(
        result["daily_min"] > 0, result["daily_max"] / result["daily_min"], np.nan
    )
    filled_max = np.where(np.isnan(values), -np.inf, values)
    filled_min = np.where(np.isnan(values), np.inf, values)
    result["max_time_index"] = filled_max.argmax(axis=1) + 1
    result["min_time_index"] = filled_min.argmin(axis=1) + 1
    result.loc[all_nan, ["daily_max", "daily_min", "daily_mean", "daily_std"]] = np.nan
    result.loc[all_nan, ["peak_valley_diff", "peak_valley_ratio"]] = np.nan
    result.loc[all_nan, ["max_time_index", "min_time_index"]] = np.nan
    result["day_load_factor"] = np.where(
        result["daily_max"] > 0, result["daily_mean"] / result["daily_max"], np.nan
    )
    result["ramp_up_count"] = (diffs > 0).sum(axis=1)
    result["ramp_down_count"] = (diffs < 0).sum(axis=1)
    result["flat_segment_count"] = (np.abs(diffs) <= 0.5).sum(axis=1)
    return result
