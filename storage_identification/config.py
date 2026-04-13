from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


RESULT_COLUMNS = ["CONS_NO", "MADE_NO", "DATA_DATE", "NULL_RATE"] + [
    f"D{i}" for i in range(1, 97)
]


@dataclass(frozen=True)
class PipelineConfig:
    dataset_root: Path
    output_root: Path

    @property
    def meter_day_curve_path(self) -> Path:
        return self.output_root / "meter_day_curve.parquet"

    @property
    def meter_day_feature_path(self) -> Path:
        return self.output_root / "meter_day_feature.parquet"

    @property
    def meter_summary_path(self) -> Path:
        return self.output_root / "meter_summary.parquet"

    @property
    def cons_summary_path(self) -> Path:
        return self.output_root / "cons_summary.parquet"
