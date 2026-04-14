from __future__ import annotations

import numpy as np
import pandas as pd


def _window_mean(values: np.ndarray, start: int, end: int) -> np.ndarray:
    return np.nanmean(values[:, start - 1 : end], axis=1)


def _pattern_similarity(curr: np.ndarray, prev: np.ndarray) -> float:
    """Return a [0, 1] shape similarity score between two 96-point load curves.

    Uses a cosine similarity over z-scored points (equivalent to Pearson corr),
    ignoring NaNs and clamping negatives to 0 to avoid penalizing unclear days.
    """

    mask = np.isfinite(curr) & np.isfinite(prev)
    if int(mask.sum()) < 48:
        return 0.0

    a = curr[mask].astype(float, copy=False)
    b = prev[mask].astype(float, copy=False)
    a = a - float(np.mean(a))
    b = b - float(np.mean(b))
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-12:
        return 0.0
    sim = float(np.dot(a, b) / denom)
    if not np.isfinite(sim):
        return 0.0
    return float(np.clip(sim, 0.0, 1.0))


def compute_storage_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for col in ["CONS_NO", "MADE_NO", "DATA_DATE"]:
        if col not in result.columns:
            raise ValueError(f"Missing required column: {col}")
    result["DATA_DATE"] = pd.to_datetime(result["DATA_DATE"], errors="coerce", format="mixed")
    result = result.sort_values(["CONS_NO", "MADE_NO", "DATA_DATE"], kind="mergesort", na_position="last").reset_index(
        drop=True
    )
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

    usable_for_feature = (
        result["usable_for_feature"].fillna(True).astype(bool)
        if "usable_for_feature" in result.columns
        else pd.Series(True, index=result.index)
    )

    recent_similarity = np.zeros(len(result), dtype=float)
    workday_repeat = np.zeros(len(result), dtype=float)
    multi_day_consistency = np.zeros(len(result), dtype=float)
    valid_date = result["DATA_DATE"].notna().to_numpy(dtype=bool)
    usable_for_repeat = (usable_for_feature.to_numpy(dtype=bool)) & valid_date

    # Repeatability is computed within meter using prior days only.
    for _, idxs in result.groupby(["CONS_NO", "MADE_NO"], dropna=False).groups.items():
        prior_usable: list[int] = []
        for idx in idxs:
            if not usable_for_repeat[idx]:
                continue

            if prior_usable:
                recent_similarity[idx] = _pattern_similarity(values[idx], values[prior_usable[-1]])

                lookback = prior_usable[-7:]
                sims = [_pattern_similarity(values[idx], values[j]) for j in lookback]
                if sims:
                    multi_day_consistency[idx] = float(np.mean(sims))

                ts = pd.Timestamp(result.at[idx, "DATA_DATE"])
                if ts.dayofweek < 5:
                    prior_workdays = [
                        j for j in reversed(lookback) if pd.Timestamp(result.at[j, "DATA_DATE"]).dayofweek < 5
                    ]
                    if prior_workdays:
                        workday_repeat[idx] = _pattern_similarity(values[idx], values[prior_workdays[0]])

            prior_usable.append(int(idx))

    # Convert raw similarities to bounded "scores" used downstream.
    result["recent_pattern_similarity"] = np.clip(recent_similarity, 0.0, 1.0)
    result["workday_repeat_score"] = np.clip(workday_repeat, 0.0, 1.0) * 5.0
    result["multi_day_consistency_score"] = np.clip(multi_day_consistency, 0.0, 1.0) * 10.0

    result["missing_penalty"] = np.where(usable_for_feature, 0.0, 20.0)
    result["noise_penalty"] = np.where(result["step_up_score"] + result["step_down_score"] > 40, 10.0, 0.0)

    base_day_score = (
        result["charge_discharge_pair_score"]
        + np.clip(result["valley_charge_score"], 0, 20)
        + np.clip(result["peak_discharge_score"], 0, 20)
        + np.clip(result["platform_score"] * 10, 0, 10)
        - result["missing_penalty"]
        - result["noise_penalty"]
    )
    repeat_applicable = (
        (result["charge_discharge_pair_score"] > 0)
        | (result["valley_charge_score"] > 0)
        | (result["peak_discharge_score"] > 0)
    )
    repeat_bonus = np.where(
        repeat_applicable,
        np.clip(result["recent_pattern_similarity"] * 5.0, 0.0, 5.0)
        + np.clip(result["multi_day_consistency_score"], 0.0, 10.0)
        + np.clip(result["workday_repeat_score"], 0.0, 5.0),
        0.0,
    )
    result["day_storage_score"] = (base_day_score + repeat_bonus).clip(lower=0, upper=100)

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
        + ";recent_sim=" + result["recent_pattern_similarity"].round(3).astype(str)
        + ";workday_rep=" + result["workday_repeat_score"].round(2).astype(str)
        + ";multi_cons=" + result["multi_day_consistency_score"].round(2).astype(str)
    )
    return result
