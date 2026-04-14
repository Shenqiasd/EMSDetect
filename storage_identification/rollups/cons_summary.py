from __future__ import annotations

import pandas as pd


CONS_SUMMARY_COLUMNS = [
    "CONS_NO",
    "meter_count",
    "active_meter_count",
    "positive_meter_count",
    "strong_positive_meter_count",
    "cons_storage_score",
    "cons_storage_label",
    "top_meter_list",
    "top_evidence_days",
    "top_hit_rules",
    "review_priority",
]


def _flatten_lists(series: pd.Series, limit: int = 5) -> list[str]:
    items: list[str] = []
    for value in series:
        if isinstance(value, list):
            items.extend(str(item) for item in value)
    return items[:limit]


def build_cons_summary(meter_summary: pd.DataFrame) -> pd.DataFrame:
    if meter_summary.empty:
        return pd.DataFrame(columns=CONS_SUMMARY_COLUMNS)

    work = meter_summary.copy()
    if "top_hit_rules" not in work.columns:
        work["top_hit_rules"] = [[] for _ in range(len(work))]
    if "meter_top_evidence_days" not in work.columns:
        work["meter_top_evidence_days"] = [[] for _ in range(len(work))]
    if "usable_day_count" not in work.columns:
        work["usable_day_count"] = 1

    grouped = work.groupby("CONS_NO", dropna=False)
    active_mask = work["usable_day_count"].fillna(0).astype(float) > 0
    strong_positive_mask = (work["meter_storage_score"].fillna(0.0) >= 80) & active_mask
    positive_mask = (work["meter_storage_score"].fillna(0.0) >= 35) & active_mask
    weak_mask = (work["meter_storage_score"].fillna(0.0) >= 30) & active_mask

    result = grouped.agg(
        meter_count=("MADE_NO", "count"),
        active_meter_count=("usable_day_count", lambda s: (s > 0).sum()),
        positive_meter_count=("MADE_NO", lambda s: int(positive_mask.loc[s.index].sum())),
        strong_positive_meter_count=("MADE_NO", lambda s: int(strong_positive_mask.loc[s.index].sum())),
        cons_storage_score=("meter_storage_score", "max"),
    ).reset_index()

    top_meters = (
        work.sort_values(["CONS_NO", "meter_storage_score"], ascending=[True, False])
        .groupby("CONS_NO", dropna=False)
        .head(3)
        .groupby("CONS_NO", dropna=False)["MADE_NO"]
        .agg(list)
        .rename("top_meter_list")
        .reset_index()
    )
    evidence_days = (
        grouped["meter_top_evidence_days"]
        .agg(_flatten_lists)
        .rename("top_evidence_days")
        .reset_index()
    )
    hit_rules = (
        grouped["top_hit_rules"]
        .agg(_flatten_lists)
        .rename("top_hit_rules")
        .reset_index()
    )

    result = result.merge(top_meters, on="CONS_NO", how="left")
    result = result.merge(evidence_days, on="CONS_NO", how="left")
    result = result.merge(hit_rules, on="CONS_NO", how="left")
    weak_evidence = (
        grouped["MADE_NO"]
        .agg(lambda s: int(weak_mask.loc[s.index].sum()) >= 2)
        .rename("weak_evidence")
        .reset_index()
    )
    result = result.merge(weak_evidence, on="CONS_NO", how="left")

    strong_positive = result["strong_positive_meter_count"] >= 1
    positive_meter = result["positive_meter_count"] >= 1
    result["cons_storage_label"] = "no_storage"
    result.loc[positive_meter | result["weak_evidence"].fillna(False), "cons_storage_label"] = "uncertain"
    result.loc[strong_positive, "cons_storage_label"] = "has_storage"
    result["review_priority"] = result["cons_storage_score"].rank(ascending=False, method="dense")

    for col in ["top_meter_list", "top_evidence_days", "top_hit_rules"]:
        result[col] = result[col].apply(lambda value: value if isinstance(value, list) else [])
    return result.loc[:, CONS_SUMMARY_COLUMNS]
