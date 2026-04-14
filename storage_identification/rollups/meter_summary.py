from __future__ import annotations

import pandas as pd


METER_SUMMARY_COLUMNS = [
    "CONS_NO",
    "MADE_NO",
    "observed_day_count",
    "strong_positive_day_count",
    "weak_positive_day_count",
    "avg_day_storage_score",
    "max_day_storage_score",
    "positive_day_ratio",
    "avg_top5_day_score",
    "meter_storage_score",
    "meter_storage_label",
    "meter_top_evidence_days",
    "usable_day_count",
]


def build_meter_summary(day_features: pd.DataFrame) -> pd.DataFrame:
    if day_features.empty:
        return pd.DataFrame(columns=METER_SUMMARY_COLUMNS)

    work = day_features.copy()
    work["DATA_DATE"] = pd.to_datetime(work["DATA_DATE"], errors="coerce", format="mixed")
    group_keys = ["CONS_NO", "MADE_NO"]
    work["_valid_day"] = work["DATA_DATE"].notna()
    work["_strong_positive_valid"] = ((work["day_label"] == "strong_positive") & work["_valid_day"]).astype(int)
    work["_weak_positive_valid"] = ((work["day_label"] == "weak_positive") & work["_valid_day"]).astype(int)
    valid_work = work.loc[work["_valid_day"]].copy()
    grouped = valid_work.groupby(group_keys, dropna=False)
    result = work.loc[:, group_keys].drop_duplicates().reset_index(drop=True)
    usable_source = (
        work["usable_for_feature"].fillna(True).astype(bool)
        if "usable_for_feature" in work.columns
        else pd.Series(True, index=work.index)
    )

    valid_summary = grouped.agg(
        observed_day_count=("DATA_DATE", "count"),
        strong_positive_day_count=("_strong_positive_valid", "sum"),
        weak_positive_day_count=("_weak_positive_valid", "sum"),
        avg_day_storage_score=("day_storage_score", "mean"),
        max_day_storage_score=("day_storage_score", "max"),
    ).reset_index()
    result = result.merge(valid_summary, on=group_keys, how="left")

    # Repeat-strong evidence should be resilient to many negative days.
    strong_avg = (
        valid_work.loc[valid_work["_strong_positive_valid"] > 0, group_keys + ["day_storage_score"]]
        .groupby(group_keys, dropna=False)["day_storage_score"]
        .mean()
        .rename("strong_positive_avg_day_score")
        .reset_index()
    )
    usable_day_count = (
        work.loc[:, group_keys]
        .assign(usable_for_feature=usable_source.astype(int))
        .groupby(group_keys, dropna=False)["usable_for_feature"]
        .sum()
        .rename("usable_day_count")
        .reset_index()
    )

    result["positive_day_ratio"] = (
        result["strong_positive_day_count"] + result["weak_positive_day_count"]
    ) / result["observed_day_count"].fillna(0).where(result["observed_day_count"].fillna(0) > 0, 1)

    top_days = (
        valid_work.sort_values(group_keys + ["day_storage_score"], ascending=[True, True, False])
        .groupby(group_keys, dropna=False)
        .head(5)
        .copy()
    )
    top_days["formatted_date"] = pd.to_datetime(top_days["DATA_DATE"]).dt.strftime("%Y-%m-%d")

    avg_top5 = (
        top_days.groupby(group_keys, dropna=False)["day_storage_score"]
        .mean()
        .rename("avg_top5_day_score")
        .reset_index()
    )
    evidence_days = (
        top_days.groupby(group_keys, dropna=False)["formatted_date"]
        .agg(list)
        .rename("meter_top_evidence_days")
        .reset_index()
    )
    result = result.merge(usable_day_count, on=group_keys, how="left")
    result = result.merge(strong_avg, on=group_keys, how="left")
    result = result.merge(avg_top5, on=group_keys, how="left")
    result = result.merge(evidence_days, on=group_keys, how="left")
    result["observed_day_count"] = result["observed_day_count"].fillna(0).astype(int)
    result["strong_positive_day_count"] = result["strong_positive_day_count"].fillna(0).astype(int)
    result["weak_positive_day_count"] = result["weak_positive_day_count"].fillna(0).astype(int)
    result["avg_day_storage_score"] = result["avg_day_storage_score"].fillna(0.0)
    result["max_day_storage_score"] = result["max_day_storage_score"].fillna(0.0)
    result["avg_top5_day_score"] = result["avg_top5_day_score"].fillna(0.0)
    result["strong_positive_avg_day_score"] = result["strong_positive_avg_day_score"].fillna(0.0)

    result["meter_storage_score"] = (
        result["avg_day_storage_score"] * 0.4
        + result["max_day_storage_score"] * 0.4
        + result["positive_day_ratio"] * 20
    ).clip(upper=100)
    result["meter_storage_label"] = result["meter_storage_score"].map(
        lambda score: "has_storage" if score >= 80 else "uncertain" if score >= 35 else "no_storage"
    )
    repeated_strong_behavior = (result["strong_positive_day_count"] >= 3) & (
        result["strong_positive_avg_day_score"] >= 75
    )
    result.loc[repeated_strong_behavior, "meter_storage_label"] = "has_storage"
    result["meter_top_evidence_days"] = result["meter_top_evidence_days"].apply(
        lambda value: value if isinstance(value, list) else []
    )
    return result.loc[:, METER_SUMMARY_COLUMNS]
