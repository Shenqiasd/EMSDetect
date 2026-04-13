from pathlib import Path

import pytest

from storage_identification.config import PipelineConfig


@pytest.fixture
def pipeline_config(tmp_path: Path) -> PipelineConfig:
    return PipelineConfig(
        dataset_root=tmp_path / "dataset",
        output_root=tmp_path / "artifacts",
    )
