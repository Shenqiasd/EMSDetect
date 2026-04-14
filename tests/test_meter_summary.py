import numpy as np
import pandas as pd

from storage_identification.rollups.meter_summary import build_meter_summary


def test_meter_summary_counts_and_uncertain_label() -> None:
    rows = [
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": pd.Timestamp("2025-08-01"),
            "day_storage_score": 70,
            "day_label": "strong_positive",
            "hit_rules": "charge_discharge_pair",
            "evidence_summary": "valley=10;peak=12",
            "usable_for_feature": True,
        },
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": pd.Timestamp("2025-08-02"),
            "day_storage_score": 45,
            "day_label": "weak_positive",
            "hit_rules": "charge_discharge_pair",
            "evidence_summary": "valley=8;peak=9",
            "usable_for_feature": True,
        },
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": pd.Timestamp("2025-08-03"),
            "day_storage_score": 10,
            "day_label": "negative",
            "hit_rules": "none",
            "evidence_summary": "valley=2;peak=1",
            "usable_for_feature": True,
        },
    ]

    summary = build_meter_summary(pd.DataFrame(rows)).iloc[0]

    assert summary["observed_day_count"] == 3
    assert summary["strong_positive_day_count"] == 1
    assert summary["weak_positive_day_count"] == 1
    assert summary["meter_storage_score"] == 58
    assert summary["meter_storage_label"] == "uncertain"
    assert summary["positive_day_ratio"] == 2 / 3
    assert summary["top_hit_rules"] == ["charge_discharge_pair", "charge_discharge_pair", "none"]


def test_meter_summary_does_not_promote_midrange_repeat_days_to_has_storage() -> None:
    rows = [
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": pd.Timestamp("2025-08-01"),
            "day_storage_score": 65,
            "day_label": "strong_positive",
            "hit_rules": "charge_discharge_pair",
            "evidence_summary": "valley=10;peak=12",
            "usable_for_feature": True,
        },
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": pd.Timestamp("2025-08-02"),
            "day_storage_score": 65,
            "day_label": "strong_positive",
            "hit_rules": "charge_discharge_pair",
            "evidence_summary": "valley=10;peak=12",
            "usable_for_feature": True,
        },
    ]

    summary = build_meter_summary(pd.DataFrame(rows)).iloc[0]

    assert summary["meter_storage_score"] == 72
    assert summary["meter_storage_label"] == "uncertain"


def test_meter_summary_normalizes_all_nan_scores_to_zero() -> None:
    rows = [
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": pd.Timestamp("2025-08-01"),
            "day_storage_score": np.nan,
            "day_label": "negative",
            "hit_rules": "none",
            "evidence_summary": "missing",
            "usable_for_feature": False,
        }
    ]

    summary = build_meter_summary(pd.DataFrame(rows)).iloc[0]

    assert summary["meter_storage_score"] == 0
    assert summary["meter_storage_label"] == "no_storage"


def test_meter_summary_excludes_null_dates_from_positive_ratio() -> None:
    rows = [
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": pd.NaT,
            "day_storage_score": 80,
            "day_label": "strong_positive",
            "hit_rules": "charge_discharge_pair",
            "evidence_summary": "null-date",
            "usable_for_feature": True,
        },
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": pd.Timestamp("2025-08-01"),
            "day_storage_score": 10,
            "day_label": "negative",
            "hit_rules": "none",
            "evidence_summary": "valid-date",
            "usable_for_feature": True,
        },
    ]

    summary = build_meter_summary(pd.DataFrame(rows)).iloc[0]

    assert summary["observed_day_count"] == 1
    assert summary["strong_positive_day_count"] == 0
    assert summary["avg_day_storage_score"] == 10
    assert summary["positive_day_ratio"] == 0
    assert summary["meter_top_evidence_days"] == ["2025-08-01"]


def test_meter_summary_excludes_invalid_date_strings_from_aggregates() -> None:
    rows = [
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": "bad-date",
            "day_storage_score": 80,
            "day_label": "strong_positive",
            "hit_rules": "charge_discharge_pair",
            "evidence_summary": "bad-date",
            "usable_for_feature": True,
        },
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": pd.Timestamp("2025-08-01"),
            "day_storage_score": 10,
            "day_label": "negative",
            "hit_rules": "none",
            "evidence_summary": "valid-date",
            "usable_for_feature": True,
        },
    ]

    summary = build_meter_summary(pd.DataFrame(rows)).iloc[0]

    assert summary["observed_day_count"] == 1
    assert summary["avg_day_storage_score"] == 10
    assert summary["meter_top_evidence_days"] == ["2025-08-01"]


def test_meter_summary_promotes_three_strong_positive_days_to_has_storage_even_with_many_negatives() -> None:
    rows = []
    for date, score in [
        (pd.Timestamp("2025-08-01"), 82),
        (pd.Timestamp("2025-08-02"), 78),
        (pd.Timestamp("2025-08-03"), 75),
    ]:
        rows.append(
            {
                "CONS_NO": "C1",
                "MADE_NO": "M1",
                "DATA_DATE": date,
                "day_storage_score": score,
                "day_label": "strong_positive",
                "hit_rules": "charge_discharge_pair",
                "evidence_summary": "strong",
                "usable_for_feature": True,
            }
        )

    # Many additional negative days should not erase repeated strong-positive evidence.
    for day in range(4, 14):
        rows.append(
            {
                "CONS_NO": "C1",
                "MADE_NO": "M1",
                "DATA_DATE": pd.Timestamp(f"2025-08-{day:02d}"),
                "day_storage_score": 0,
                "day_label": "negative",
                "hit_rules": "none",
                "evidence_summary": "neg",
                "usable_for_feature": True,
            }
        )

    summary = build_meter_summary(pd.DataFrame(rows)).iloc[0]

    assert summary["strong_positive_day_count"] == 3
    assert summary["meter_storage_label"] == "has_storage"


def test_meter_summary_keeps_top_hit_rules_for_rollup_evidence() -> None:
    rows = [
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": pd.Timestamp("2025-08-01"),
            "day_storage_score": 70,
            "day_label": "strong_positive",
            "hit_rules": "charge_discharge_pair",
            "evidence_summary": "strong",
            "usable_for_feature": True,
        },
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": pd.Timestamp("2025-08-02"),
            "day_storage_score": 40,
            "day_label": "weak_positive",
            "hit_rules": "valley_charge_only",
            "evidence_summary": "weak",
            "usable_for_feature": True,
        },
    ]

    summary = build_meter_summary(pd.DataFrame(rows)).iloc[0]

    assert summary["top_hit_rules"] == ["charge_discharge_pair", "valley_charge_only"]
