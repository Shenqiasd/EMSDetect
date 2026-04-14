from __future__ import annotations

import numpy as np
import pandas as pd


def _window_mean(values: np.ndarray, start: int, end: int) -> np.ndarray:
    return np.nanmean(values[:, start - 1 : end], axis=1)


def compute_storage_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    curve_cols = [f"D{idx}" for idx in range(1, 97)]
    if not any(col in result.columns for col in curve_cols):
        raise ValueError("No valid curve columns found. Expected D1..D96.")
    values = result.reindex(columns=curve_cols).to_numpy(dtype=float)
    baseline = np.nanmean(values, axis=1)

    valley_mean = _window_mean(values, 10, 20)
    midday_mean = _window_mean(values, 40, 52)
    peak_mean = _window_mean(values, 70, 80)
    evening_mean = _window_mean(values, 76, 88)

    result["valley_charge_score"] = np.nan_to_num(np.clip(valley_mean - baseline, 0, None) * 5, nan=0.0)
    result["midday_charge_score"] = np.nan_to_num(np.clip(midday_mean - baseline, 0, None) * 5, nan=0.0)
    result["peak_discharge_score"] = np.nan_to_num(np.clip(baseline - peak_mean, 0, None) * 5, nan=0.0)
    result["evening_discharge_score"] = np.nan_to_num(np.clip(baseline - evening_mean, 0, None) * 5, nan=0.0)

    diffs = np.diff(values, axis=1)
    result["step_up_score"] = (diffs > 1.5).sum(axis=1)
    result["step_down_score"] = (diffs < -1.5).sum(axis=1)
    result["platform_score"] = (np.abs(diffs) <= 0.3).sum(axis=1) / max(1, diffs.shape[1])
    result["charge_discharge_pair_score"] = np.where(
        (result["valley_charge_score"] > 0) & (result["peak_discharge_score"] > 0),
        35,
        0,
    )

    result["recent_pattern_similarity"] = 0.0
    result["workday_repeat_score"] = 0.0
    result["multi_day_consistency_score"] = 0.0
    usable_for_feature = (
        result["usable_for_feature"].fillna(True).astype(bool)
        if "usable_for_feature" in result.columns
        else pd.Series(True, index=result.index)
    )
    result["missing_penalty"] = np.where(usable_for_feature, 0.0, 20.0)
    result["noise_penalty"] = np.where(result["step_up_score"] + result["step_down_score"] > 40, 10.0, 0.0)

    result["day_storage_score"] = (
        result["charge_discharge_pair_score"]
        + np.clip(result["valley_charge_score"], 0, 20)
        + np.clip(result["peak_discharge_score"], 0, 20)
        + np.clip(result["platform_score"] * 10, 0, 10)
        - result["missing_penalty"]
        - result["noise_penalty"]
    ).clip(lower=0, upper=100)

    result["day_label"] = np.select(
        [
            result["day_storage_score"] >= 60,
            result["day_storage_score"] >= 35,
        ],
        [
            "strong_positive",
            "weak_positive",
        ],
        default="negative",
    )
    result["hit_rules"] = np.where(
        result["charge_discharge_pair_score"] > 0,
        "charge_discharge_pair",
        "none",
    )
    result["evidence_summary"] = (
        "valley=" + result["valley_charge_score"].round(2).astype(str)
        + ";peak=" + result["peak_discharge_score"].round(2).astype(str)
    )
    return result
