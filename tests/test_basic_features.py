import numpy as np
import pandas as pd

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
