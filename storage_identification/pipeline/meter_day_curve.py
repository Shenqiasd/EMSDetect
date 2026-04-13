from __future__ import annotations

import pandas as pd

KEY_COLUMNS = ["CONS_NO", "MADE_NO", "DATA_DATE"]


def build_meter_day_curve(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    curve_cols = [col for col in df.columns if col.startswith("D") and col != "DATA_DATE"]

    df["NULL_RATE"] = pd.to_numeric(df["NULL_RATE"], errors="coerce").fillna(1.0)
    df["DATA_DATE"] = pd.to_datetime(df["DATA_DATE"], format="%Y/%m/%d")
    for col in curve_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = (
        df.sort_values("NULL_RATE", ascending=True)
        .drop_duplicates(subset=KEY_COLUMNS, keep="first")
        .reset_index(drop=True)
    )

    df["month"] = df["DATA_DATE"].dt.month
    df["day_of_week"] = df["DATA_DATE"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6])
    df["is_full_null"] = df["NULL_RATE"] >= 1.0
    df["is_partial_null"] = (df["NULL_RATE"] > 0) & (df["NULL_RATE"] < 1.0)
    df["usable_for_feature"] = df["NULL_RATE"] < 0.5
    return df
