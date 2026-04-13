from __future__ import annotations

import pandas as pd

KEY_COLUMNS = ["CONS_NO", "MADE_NO", "DATA_DATE"]
DEDUPE_KEY_COLUMNS = ["CONS_NO", "MADE_NO", "_raw_data_date"]


def build_meter_day_curve(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    curve_cols = [f"D{idx}" for idx in range(1, 97) if f"D{idx}" in df.columns]

    df["_raw_data_date"] = df["DATA_DATE"].astype(str)
    df["NULL_RATE"] = pd.to_numeric(df["NULL_RATE"], errors="coerce").fillna(1.0)
    df["DATA_DATE"] = pd.to_datetime(df["DATA_DATE"], format="%Y/%m/%d", errors="coerce")
    for col in curve_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if curve_cols:
        df["_curve_missing_rate"] = df[curve_cols].isna().mean(axis=1)
    else:
        df["_curve_missing_rate"] = 1.0
    df["_invalid_date"] = df["DATA_DATE"].isna()
    df["_effective_null_rate"] = df[["NULL_RATE", "_curve_missing_rate"]].max(axis=1)

    df = (
        df.sort_values(
            ["_effective_null_rate", "_curve_missing_rate", "_invalid_date", "NULL_RATE", *curve_cols, "_raw_data_date"],
            ascending=True,
        )
        .drop_duplicates(subset=DEDUPE_KEY_COLUMNS, keep="first")
        .reset_index(drop=True)
    )

    df["month"] = df["DATA_DATE"].dt.month
    df["day_of_week"] = df["DATA_DATE"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6])
    df["is_full_null"] = df["_effective_null_rate"] >= 1.0
    df["is_partial_null"] = (df["_effective_null_rate"] > 0) & (df["_effective_null_rate"] < 1.0)
    df["usable_for_feature"] = (df["_effective_null_rate"] < 0.5) & (~df["_invalid_date"])
    df = df.drop(columns=["_curve_missing_rate", "_effective_null_rate", "_invalid_date", "_raw_data_date"])
    return df
