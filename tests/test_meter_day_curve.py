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


def test_build_meter_day_curve_uses_curve_missingness() -> None:
    raw = pd.DataFrame(
        [
            {
                "CONS_NO": "C2",
                "MADE_NO": "M3",
                "DATA_DATE": "2025/8/3",
                "NULL_RATE": 0.0,
                "D1": "5",
                "D2": "bad",
                "D3": None,
            }
        ]
    )

    result = build_meter_day_curve(raw)

    assert result.loc[0, "is_partial_null"].item() is True
    assert result.loc[0, "is_full_null"].item() is False
    assert result.loc[0, "usable_for_feature"].item() is False


def test_build_meter_day_curve_handles_invalid_date() -> None:
    raw = pd.DataFrame(
        [
            {
                "CONS_NO": "C3",
                "MADE_NO": "M4",
                "DATA_DATE": "bad-date",
                "NULL_RATE": 0.0,
                "D1": "1",
                "D2": "2",
            }
        ]
    )

    result = build_meter_day_curve(raw)

    assert pd.isna(result.loc[0, "month"])
    assert result.loc[0, "usable_for_feature"].item() is False


def test_build_meter_day_curve_dedup_tie_breaks_by_quality() -> None:
    raw = pd.DataFrame(
        [
            {
                "CONS_NO": "C4",
                "MADE_NO": "M5",
                "DATA_DATE": "2025/8/4",
                "NULL_RATE": 0.2,
                "D1": "bad",
                "D2": "3",
            },
            {
                "CONS_NO": "C4",
                "MADE_NO": "M5",
                "DATA_DATE": "2025/8/4",
                "NULL_RATE": 0.2,
                "D1": "1",
                "D2": "3",
            },
        ]
    )

    result = build_meter_day_curve(raw)

    assert result.loc[0, "D1"] == 1


def test_build_meter_day_curve_ignores_non_contract_columns() -> None:
    raw = pd.DataFrame(
        [
            {
                "CONS_NO": "C5",
                "MADE_NO": "M6",
                "DATA_DATE": "2025/8/5",
                "NULL_RATE": 0.0,
                "D1": "1",
                "D100": "bad",
            }
        ]
    )

    result = build_meter_day_curve(raw)

    assert result.loc[0, "usable_for_feature"].item() is True
