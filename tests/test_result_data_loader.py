from pathlib import Path

from storage_identification.config import PipelineConfig


def test_pipeline_config_points_to_expected_output_layers(tmp_path: Path) -> None:
    cfg = PipelineConfig(
        dataset_root=tmp_path / "dataset",
        output_root=tmp_path / "artifacts",
    )

    assert cfg.meter_day_curve_path.name == "meter_day_curve.parquet"
    assert cfg.meter_day_feature_path.name == "meter_day_feature.parquet"
    assert cfg.meter_summary_path.name == "meter_summary.parquet"
    assert cfg.cons_summary_path.name == "cons_summary.parquet"
