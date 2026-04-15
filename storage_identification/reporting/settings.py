from __future__ import annotations

import os
from pathlib import Path


def default_data_root() -> Path:
    env_value = os.environ.get("STORAGE_REPORT_DATA_DIR")
    if env_value:
        return Path(env_value)
    return Path(__file__).resolve().parent / "demo_data"


def default_template_dir() -> Path:
    return Path(__file__).resolve().parent / "templates"


def default_static_dir() -> Path:
    return Path(__file__).resolve().parent / "static"
