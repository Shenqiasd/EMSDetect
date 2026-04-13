import pandas as pd

from storage_identification.pipeline.meter_day_curve import build_meter_day_curve


def test_build_meter_day_curve_deduplicates_and_flags_quality() -> None:
    raw = pd.DataFrame(
        [
            {"CONS_NO": "C1", "MADE_NO": "M1", "DATA_DATE": "2025/8/1", "NULL_RATE": 0.3, "D1": "10", "D2": "12"},
            {"CONS_NO": "C1", "MADE_NO": "M1", "DATA_DATE": "2025/8/1", "NULL_RATE": 0.1, "D1": "10", "D2": "12"},
            {"CONS_NO": "C1", "MADE_NO": "M2", "DATA_DATE": "2025/8/2", "NULL_RATE": 0.6, "D1": "8", "D2": "9"},
        ]
    )

    result = build_meter_day_curve(raw)

    assert len(result) == 2
    assert result.loc[result["MADE_NO"] == "M1", "NULL_RATE"].item() == 0.1
    assert result.loc[result["MADE_NO"] == "M1", "usable_for_feature"].item() is True
    assert result.loc[result["MADE_NO"] == "M2", "usable_for_feature"].item() is False
