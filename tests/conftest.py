from pathlib import Path
from uuid import uuid4

import pytest

from storage_identification.config import PipelineConfig

TMP_ROOT = Path(__file__).resolve().parents[1] / ".task1-pytest-tmp"


@pytest.fixture
def tmp_path() -> Path:
    TMP_ROOT.mkdir(exist_ok=True)
    tmpdir = TMP_ROOT / uuid4().hex
    tmpdir.mkdir()
    return tmpdir


@pytest.fixture
def pipeline_config(tmp_path: Path) -> PipelineConfig:
    return PipelineConfig(
        dataset_root=tmp_path / "dataset",
        output_root=tmp_path / "artifacts",
    )
