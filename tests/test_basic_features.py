import numpy as np
import pandas as pd
import pytest

from storage_identification.features.basic_features import compute_basic_features


def test_compute_basic_features_adds_core_statistics() -> None:
    df = pd.DataFrame(
        [
            {
                "CONS_NO": "C1",
                "MADE_NO": "M1",
                "DATA_DATE": pd.Timestamp("2025-08-01"),
                "D1": 10.0,
                "D2": 14.0,
                "D3": 6.0,
            }
        ]
    )

    result = compute_basic_features(df)

    assert result["daily_max"].item() == 14.0
    assert result["daily_min"].item() == 6.0
    assert result["daily_mean"].item() == 10.0
    assert np.isclose(result["daily_std"].item(), 3.2659863237)
    assert result["peak_valley_diff"].item() == 8.0
    assert np.isclose(result["peak_valley_ratio"].item(), 14.0 / 6.0)
    assert result["max_time_index"].item() == 2
    assert result["min_time_index"].item() == 3
    assert np.isclose(result["day_load_factor"].item(), 10.0 / 14.0)
    assert result["ramp_up_count"].item() == 1
    assert result["ramp_down_count"].item() == 1
    assert result["flat_segment_count"].item() == 0


def test_compute_basic_features_handles_partial_nan() -> None:
    df = pd.DataFrame(
        [
            {
                "CONS_NO": "C1",
                "MADE_NO": "M1",
                "DATA_DATE": pd.Timestamp("2025-08-01"),
                "D1": 10.0,
                "D2": np.nan,
                "D3": 6.0,
            },
            {
                "CONS_NO": "C2",
                "MADE_NO": "M2",
                "DATA_DATE": pd.Timestamp("2025-08-01"),
                "D1": np.nan,
                "D2": np.nan,
                "D3": np.nan,
            },
        ]
    )

    result = compute_basic_features(df)

    assert result["daily_max"].iloc[0] == 10.0
    assert result["daily_min"].iloc[0] == 6.0
    assert result["daily_mean"].iloc[0] == 8.0
    assert np.isclose(result["daily_std"].iloc[0], 2.0)
    assert result["peak_valley_diff"].iloc[0] == 4.0
    assert np.isclose(result["peak_valley_ratio"].iloc[0], 10.0 / 6.0)
    assert result["max_time_index"].iloc[0] == 1
    assert result["min_time_index"].iloc[0] == 3
    assert np.isclose(result["day_load_factor"].iloc[0], 8.0 / 10.0)
    assert result["ramp_up_count"].iloc[0] == 0
    assert result["ramp_down_count"].iloc[0] == 0
    assert result["flat_segment_count"].iloc[0] == 0

    assert np.isnan(result["daily_max"].iloc[1])
    assert np.isnan(result["daily_min"].iloc[1])
    assert np.isnan(result["daily_mean"].iloc[1])
    assert np.isnan(result["daily_std"].iloc[1])
    assert np.isnan(result["peak_valley_diff"].iloc[1])
    assert np.isnan(result["peak_valley_ratio"].iloc[1])
    assert np.isnan(result["max_time_index"].iloc[1])
    assert np.isnan(result["min_time_index"].iloc[1])
    assert np.isnan(result["day_load_factor"].iloc[1])
    assert result["ramp_up_count"].iloc[1] == 0
    assert result["ramp_down_count"].iloc[1] == 0
    assert result["flat_segment_count"].iloc[1] == 0


def test_compute_basic_features_orders_curve_columns() -> None:
    df = pd.DataFrame(
        [
            {
                "CONS_NO": "C1",
                "MADE_NO": "M1",
                "DATA_DATE": pd.Timestamp("2025-08-01"),
                "D2": 5.0,
                "D1": 1.0,
                "D3": 9.0,
            }
        ]
    )

    result = compute_basic_features(df)

    assert result["daily_max"].item() == 9.0
    assert result["daily_min"].item() == 1.0
    assert result["daily_mean"].item() == 5.0
    assert np.isclose(result["daily_std"].item(), 3.2659863237)
    assert result["max_time_index"].item() == 3
    assert result["min_time_index"].item() == 1
    assert result["ramp_up_count"].item() == 2
    assert result["ramp_down_count"].item() == 0
    assert result["flat_segment_count"].item() == 0


def test_compute_basic_features_requires_curve_columns() -> None:
    df = pd.DataFrame(
        [
            {
                "CONS_NO": "C1",
                "MADE_NO": "M1",
                "DATA_DATE": pd.Timestamp("2025-08-01"),
                "D97": 10.0,
            }
        ]
    )

    with pytest.raises(ValueError, match="No valid curve columns"):
        compute_basic_features(df)
