from pathlib import Path

import pytest

from storage_identification.config import PipelineConfig, RESULT_COLUMNS
from storage_identification.io.result_data_loader import load_all_result_data


def test_pipeline_config_points_to_expected_output_layers(tmp_path: Path) -> None:
    cfg = PipelineConfig(
        dataset_root=tmp_path / "dataset",
        output_root=tmp_path / "artifacts",
    )

    assert cfg.meter_day_curve_path.name == "meter_day_curve.parquet"
    assert cfg.meter_day_feature_path.name == "meter_day_feature.parquet"
    assert cfg.meter_summary_path.name == "meter_summary.parquet"
    assert cfg.cons_summary_path.name == "cons_summary.parquet"


def test_load_all_result_data_unions_all_result_csvs(pipeline_config) -> None:
    data_root = pipeline_config.dataset_root
    first_dir = data_root / "2025-08" / "batch-1" / "result-data"
    second_dir = data_root / "2025-09" / "result-data"
    first_dir.mkdir(parents=True)
    second_dir.mkdir(parents=True)

    content = (
        "TG_NO,TG_NAME,CONS_NO,MADE_NO,DATA_DATE,NULL_RATE,D1,D2\n"
        ",,C1,M1,2025/8/1,0.0,10,12\n"
    )
    (first_dir / "part1.csv").write_text(content, encoding="utf-8")
    (second_dir / "part2.csv").write_text(
        content.replace("2025/8/1", "2025/9/1"),
        encoding="utf-8",
    )

    df = load_all_result_data(data_root)

    assert list(df.columns) == RESULT_COLUMNS
    assert len(df) == 2
    assert sorted(df["DATA_DATE"].tolist()) == ["2025/8/1", "2025/9/1"]


def test_load_all_result_data_returns_empty_result_columns(pipeline_config) -> None:
    df = load_all_result_data(pipeline_config.dataset_root)

    assert list(df.columns) == RESULT_COLUMNS
    assert df.empty


def test_load_all_result_data_rejects_missing_required_columns(pipeline_config) -> None:
    data_root = pipeline_config.dataset_root
    result_dir = data_root / "2025-10" / "result-data"
    result_dir.mkdir(parents=True)

    content = "TG_NO,TG_NAME,MADE_NO,DATA_DATE,NULL_RATE,D1\n,,M1,2025/10/1,0.0,10\n"
    (result_dir / "bad.csv").write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match="Missing required columns"):
        load_all_result_data(data_root)


def test_load_all_result_data_supports_chinese_result_directory_name(pipeline_config) -> None:
    data_root = pipeline_config.dataset_root
    result_dir = data_root / "2025年9月" / "结果数据"
    result_dir.mkdir(parents=True)

    content = (
        "TG_NO,TG_NAME,CONS_NO,MADE_NO,DATA_DATE,NULL_RATE,D1,D2\n"
        ",,C1,M1,2025/9/1,0.0,10,12\n"
    )
    (result_dir / "part1.csv").write_text(content, encoding="utf-8")

    df = load_all_result_data(data_root)

    assert list(df.columns) == RESULT_COLUMNS
    assert len(df) == 1
    assert df["CONS_NO"].tolist() == ["C1"]
