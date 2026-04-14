import numpy as np
import pandas as pd

from storage_identification.features.storage_features import compute_storage_features


def test_compute_storage_features_scores_charge_discharge_pair() -> None:
    row = {
        "CONS_NO": "C1",
        "MADE_NO": "M1",
        "DATA_DATE": pd.Timestamp("2025-08-01"),
        "usable_for_feature": True,
    }
    for i in range(1, 97):
        if 10 <= i <= 20:
            row[f"D{i}"] = 5.0
        elif 70 <= i <= 80:
            row[f"D{i}"] = 2.0
        else:
            row[f"D{i}"] = 3.0

    result = compute_storage_features(pd.DataFrame([row]))

    assert result["valley_charge_score"].item() > 0
    assert result["peak_discharge_score"].item() > 0
    assert result["day_storage_score"].item() >= 35
    assert result["day_label"].item() in {"weak_positive", "strong_positive"}


def test_compute_storage_features_uses_d1_to_d96_numeric_order() -> None:
    row = {
        "CONS_NO": "C1",
        "MADE_NO": "M1",
        "DATA_DATE": pd.Timestamp("2025-08-01"),
        "usable_for_feature": True,
    }
    for i in range(1, 97):
        if 10 <= i <= 20:
            row[f"D{i}"] = 5.0
        elif 70 <= i <= 80:
            row[f"D{i}"] = 2.0
        else:
            row[f"D{i}"] = 3.0

    curve_cols = [f"D{i}" for i in range(96, 0, -1)]
    df = pd.DataFrame([row]).loc[:, ["CONS_NO", "MADE_NO", "DATA_DATE", "usable_for_feature", *curve_cols]]

    result = compute_storage_features(df)

    assert result["valley_charge_score"].item() > 0
    assert result["peak_discharge_score"].item() > 0


def test_compute_storage_features_defaults_missing_quality_flag() -> None:
    row = {
        "CONS_NO": "C1",
        "MADE_NO": "M1",
        "DATA_DATE": pd.Timestamp("2025-08-01"),
    }
    for i in range(1, 97):
        row[f"D{i}"] = 3.0

    result = compute_storage_features(pd.DataFrame([row]))

    assert result["missing_penalty"].item() == 0.0
    assert pd.notna(result["day_storage_score"].item())


def test_compute_storage_features_ignores_partial_nan_curve_points() -> None:
    row = {
        "CONS_NO": "C1",
        "MADE_NO": "M1",
        "DATA_DATE": pd.Timestamp("2025-08-01"),
        "usable_for_feature": True,
    }
    for i in range(1, 97):
        if 10 <= i <= 20:
            row[f"D{i}"] = 5.0
        elif 70 <= i <= 80:
            row[f"D{i}"] = 2.0
        else:
            row[f"D{i}"] = 3.0
    row["D1"] = np.nan
    row["D96"] = np.nan

    result = compute_storage_features(pd.DataFrame([row]))

    assert pd.notna(result["day_storage_score"].item())
    assert result["day_storage_score"].item() >= 35


def test_compute_storage_features_treats_missing_curve_columns_as_missing_points() -> None:
    row = {
        "CONS_NO": "C1",
        "MADE_NO": "M1",
        "DATA_DATE": pd.Timestamp("2025-08-01"),
        "usable_for_feature": True,
    }
    for i in range(1, 97):
        if 10 <= i <= 20:
            row[f"D{i}"] = 5.0
        elif 70 <= i <= 80:
            row[f"D{i}"] = 2.0
        else:
            row[f"D{i}"] = 3.0

    with_nan_row = dict(row)
    with_nan_row["D1"] = np.nan
    with_nan_row["D96"] = np.nan
    missing_column_row = {key: value for key, value in row.items() if key not in {"D1", "D96"}}

    with_nan_result = compute_storage_features(pd.DataFrame([with_nan_row]))
    missing_column_result = compute_storage_features(pd.DataFrame([missing_column_row]))

    assert missing_column_result["valley_charge_score"].item() == with_nan_result["valley_charge_score"].item()
    assert missing_column_result["peak_discharge_score"].item() == with_nan_result["peak_discharge_score"].item()
    assert missing_column_result["day_storage_score"].item() == with_nan_result["day_storage_score"].item()


def test_compute_storage_features_marks_non_hit_days_and_keeps_expected_fields() -> None:
    row = {
        "CONS_NO": "C1",
        "MADE_NO": "M1",
        "DATA_DATE": pd.Timestamp("2025-08-01"),
        "usable_for_feature": True,
    }
    for i in range(1, 97):
        row[f"D{i}"] = 3.0

    result = compute_storage_features(pd.DataFrame([row]))

    expected_columns = {
        "valley_charge_score",
        "midday_charge_score",
        "peak_discharge_score",
        "evening_discharge_score",
        "step_up_score",
        "step_down_score",
        "platform_score",
        "charge_discharge_pair_score",
        "missing_penalty",
        "noise_penalty",
        "day_storage_score",
        "day_label",
        "hit_rules",
        "evidence_summary",
    }

    assert expected_columns.issubset(result.columns)
    assert result["hit_rules"].item() == "none"
    assert result["day_label"].item() == "negative"


def test_compute_storage_features_applies_noise_penalty_and_clips_at_zero() -> None:
    row = {
        "CONS_NO": "C1",
        "MADE_NO": "M1",
        "DATA_DATE": pd.Timestamp("2025-08-01"),
        "usable_for_feature": False,
    }
    for i in range(1, 97):
        row[f"D{i}"] = 6.0 if i % 2 == 0 else 0.0

    result = compute_storage_features(pd.DataFrame([row]))

    assert result["noise_penalty"].item() == 10.0
    assert result["missing_penalty"].item() == 20.0
    assert result["day_storage_score"].item() == 0.0


def test_compute_storage_features_rewards_repeatable_patterns_across_days() -> None:
    rows: list[dict] = []
    for date in [pd.Timestamp("2025-08-01"), pd.Timestamp("2025-08-02")]:
        row = {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": date,
            "usable_for_feature": True,
        }
        for i in range(1, 97):
            if 10 <= i <= 20:
                row[f"D{i}"] = 4.0
            elif 70 <= i <= 80:
                row[f"D{i}"] = 2.0
            else:
                row[f"D{i}"] = 3.0
        rows.append(row)

    result = compute_storage_features(pd.DataFrame(rows)).reset_index(drop=True)

    assert result.loc[0, "multi_day_consistency_score"] == 0.0
    assert result.loc[1, "recent_pattern_similarity"] > 0.0
    assert result.loc[1, "multi_day_consistency_score"] > 0.0
    assert result.loc[1, "day_storage_score"] - result.loc[0, "day_storage_score"] > 10.0


def test_compute_storage_features_skips_invalid_dates_in_repeatability_logic() -> None:
    rows: list[dict] = []
    for date in ["bad-date", pd.Timestamp("2025-08-02")]:
        row = {
            "CONS_NO": "C1",
            "MADE_NO": "M1",
            "DATA_DATE": date,
            "usable_for_feature": True,
        }
        for i in range(1, 97):
            if 10 <= i <= 20:
                row[f"D{i}"] = 4.0
            elif 70 <= i <= 80:
                row[f"D{i}"] = 2.0
            else:
                row[f"D{i}"] = 3.0
        rows.append(row)

    result = compute_storage_features(pd.DataFrame(rows)).reset_index(drop=True)

    assert result.loc[1, "recent_pattern_similarity"] == 0.0
    assert result.loc[1, "multi_day_consistency_score"] == 0.0
