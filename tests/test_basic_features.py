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
    assert result["peak_valley_diff"].item() == 8.0
