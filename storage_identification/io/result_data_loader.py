from __future__ import annotations

from pathlib import Path

import pandas as pd

from storage_identification.config import RESULT_COLUMNS

REQUIRED_RESULT_COLUMNS = ("CONS_NO", "MADE_NO", "DATA_DATE", "NULL_RATE")
RESULT_DIR_NAMES = {"result-data", "结果数据"}


def _discover_result_csvs(dataset_root: Path) -> list[Path]:
    return sorted(
        path
        for path in dataset_root.rglob("*.csv")
        if path.parent.name in RESULT_DIR_NAMES
    )


def load_all_result_data(dataset_root: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in _discover_result_csvs(dataset_root):
        frame = pd.read_csv(path, encoding="utf-8-sig")
        missing = [col for col in REQUIRED_RESULT_COLUMNS if col not in frame.columns]
        if missing:
            missing_list = ", ".join(missing)
            raise ValueError(f"Missing required columns in {path}: {missing_list}")
        frames.append(frame.reindex(columns=RESULT_COLUMNS))
    if not frames:
        return pd.DataFrame(columns=RESULT_COLUMNS)
    return pd.concat(frames, ignore_index=True)
