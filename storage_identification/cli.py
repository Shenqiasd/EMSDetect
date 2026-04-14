from __future__ import annotations

import importlib.util

from storage_identification.config import PipelineConfig
from storage_identification.features.basic_features import compute_basic_features
from storage_identification.features.storage_features import compute_storage_features
from storage_identification.io.result_data_loader import load_all_result_data
from storage_identification.pipeline.meter_day_curve import build_meter_day_curve
from storage_identification.rollups.cons_summary import build_cons_summary
from storage_identification.rollups.meter_summary import build_meter_summary


def _ensure_parquet_engine() -> None:
    if importlib.util.find_spec("pyarrow") is None and importlib.util.find_spec("fastparquet") is None:
        raise ImportError(
            "Parquet support requires 'pyarrow' or 'fastparquet'. "
            "Install one of them before running the pipeline."
        )


def run_pipeline(config: PipelineConfig) -> None:
    _ensure_parquet_engine()
    config.output_root.mkdir(parents=True, exist_ok=True)

    raw = load_all_result_data(config.dataset_root)
    meter_day_curve = build_meter_day_curve(raw)
    meter_day_curve.to_parquet(config.meter_day_curve_path, index=False)

    basic_features = compute_basic_features(meter_day_curve)
    day_features = compute_storage_features(basic_features)
    day_features.to_parquet(config.meter_day_feature_path, index=False)

    meter_summary = build_meter_summary(day_features)
    meter_summary.to_parquet(config.meter_summary_path, index=False)

    cons_summary = build_cons_summary(meter_summary)
    cons_summary.to_parquet(config.cons_summary_path, index=False)
