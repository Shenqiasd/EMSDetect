from pathlib import Path

import pandas as pd
import pytest

from storage_identification.cli import run_pipeline


def test_run_pipeline_writes_all_output_layers(pipeline_config, monkeypatch) -> None:
    result_dir = pipeline_config.dataset_root / "2025-09" / "result-data"
    result_dir.mkdir(parents=True)
    df = pd.DataFrame(
        [
            {
                "TG_NO": "",
                "TG_NAME": "",
                "CONS_NO": "C1",
                "MADE_NO": "M1",
                "DATA_DATE": "2025/9/1",
                "NULL_RATE": 0.0,
                **{f"D{i}": 3.0 for i in range(1, 97)},
            }
        ]
    )
    df.to_csv(result_dir / "sample.csv", index=False, encoding="utf-8-sig")

    def fake_to_parquet(self: pd.DataFrame, path: Path, index: bool = False) -> None:
        del self, index
        Path(path).write_text("parquet-placeholder", encoding="utf-8")

    monkeypatch.setattr("storage_identification.cli._ensure_parquet_engine", lambda: None)
    monkeypatch.setattr(pd.DataFrame, "to_parquet", fake_to_parquet)

    run_pipeline(pipeline_config)

    assert pipeline_config.meter_day_curve_path.exists()
    assert pipeline_config.meter_day_feature_path.exists()
    assert pipeline_config.meter_summary_path.exists()
    assert pipeline_config.cons_summary_path.exists()


def test_run_pipeline_raises_clear_error_without_parquet_engine(pipeline_config, monkeypatch) -> None:
    result_dir = pipeline_config.dataset_root / "2025-09" / "result-data"
    result_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "TG_NO": "",
                "TG_NAME": "",
                "CONS_NO": "C1",
                "MADE_NO": "M1",
                "DATA_DATE": "2025/9/1",
                "NULL_RATE": 0.0,
                **{f"D{i}": 3.0 for i in range(1, 97)},
            }
        ]
    ).to_csv(result_dir / "sample.csv", index=False, encoding="utf-8-sig")

    monkeypatch.setattr("storage_identification.cli.importlib.util.find_spec", lambda name: None)

    with pytest.raises(ImportError, match="Parquet support requires 'pyarrow' or 'fastparquet'"):
        run_pipeline(pipeline_config)
