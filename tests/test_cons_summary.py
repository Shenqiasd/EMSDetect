import pandas as pd

from storage_identification.rollups.cons_summary import build_cons_summary


def test_cons_summary_prefers_has_storage_label_and_counts_strong_meters() -> None:
    rows = [
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "usable_day_count": 30,
            "meter_storage_score": 85,
            "meter_storage_label": "uncertain",
            "positive_day_ratio": 0.8,
            "meter_top_evidence_days": ["2025-08-01"],
            "top_hit_rules": ["charge_discharge_pair"],
        },
        {
            "CONS_NO": "C1",
            "MADE_NO": "M2",
            "usable_day_count": 15,
            "meter_storage_score": 15,
            "meter_storage_label": "no_storage",
            "positive_day_ratio": 0.1,
            "meter_top_evidence_days": ["2025-08-02"],
            "top_hit_rules": ["none"],
        },
    ]

    summary = build_cons_summary(pd.DataFrame(rows)).iloc[0]

    assert summary["meter_count"] == 2
    assert summary["strong_positive_meter_count"] == 1
    assert summary["cons_storage_score"] == 85
    assert summary["cons_storage_label"] == "has_storage"
    assert summary["review_priority"] == 1.0


def test_cons_summary_counts_uncertain_meter_as_positive() -> None:
    rows = [
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "usable_day_count": 10,
            "meter_storage_score": 40,
            "meter_storage_label": "uncertain",
            "positive_day_ratio": 0.4,
            "meter_top_evidence_days": ["2025-08-01"],
            "top_hit_rules": ["charge_discharge_pair"],
        },
        {
            "CONS_NO": "C1",
            "MADE_NO": "M2",
            "usable_day_count": 8,
            "meter_storage_score": 15,
            "meter_storage_label": "no_storage",
            "positive_day_ratio": 0.0,
            "meter_top_evidence_days": ["2025-08-02"],
            "top_hit_rules": ["none"],
        },
    ]

    summary = build_cons_summary(pd.DataFrame(rows)).iloc[0]

    assert summary["positive_meter_count"] == 1
    assert summary["cons_storage_label"] == "uncertain"


def test_cons_summary_counts_only_usable_meters_as_active() -> None:
    rows = [
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "usable_day_count": 5,
            "meter_storage_score": 40,
            "meter_storage_label": "uncertain",
            "positive_day_ratio": 0.4,
            "meter_top_evidence_days": ["2025-08-01"],
            "top_hit_rules": ["charge_discharge_pair"],
        },
        {
            "CONS_NO": "C1",
            "MADE_NO": "M2",
            "usable_day_count": 0,
            "meter_storage_score": 5,
            "meter_storage_label": "no_storage",
            "positive_day_ratio": 0.0,
            "meter_top_evidence_days": ["2025-08-02"],
            "top_hit_rules": ["none"],
        },
    ]

    summary = build_cons_summary(pd.DataFrame(rows)).iloc[0]

    assert summary["meter_count"] == 2
    assert summary["active_meter_count"] == 1


def test_cons_summary_marks_uncertain_when_weak_evidence_accumulates() -> None:
    rows = [
        {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "usable_day_count": 10,
            "meter_storage_score": 32,
            "meter_storage_label": "no_storage",
            "positive_day_ratio": 0.2,
            "meter_top_evidence_days": ["2025-08-01"],
            "top_hit_rules": ["none"],
        },
        {
            "CONS_NO": "C1",
            "MADE_NO": "M2",
            "usable_day_count": 10,
            "meter_storage_score": 32,
            "meter_storage_label": "no_storage",
            "positive_day_ratio": 0.2,
            "meter_top_evidence_days": ["2025-08-02"],
            "top_hit_rules": ["none"],
        },
    ]

    summary = build_cons_summary(pd.DataFrame(rows)).iloc[0]

    assert summary["cons_storage_label"] == "uncertain"
