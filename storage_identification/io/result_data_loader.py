from __future__ import annotations

from pathlib import Path

import pandas as pd

from storage_identification.config import RESULT_COLUMNS


def _discover_result_csvs(dataset_root: Path) -> list[Path]:
    return sorted(
        path
        for path in dataset_root.rglob("*.csv")
        if path.parent.name == "result-data"
    )


def load_all_result_data(dataset_root: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in _discover_result_csvs(dataset_root):
        frame = pd.read_csv(path, encoding="utf-8-sig")
        frames.append(frame.loc[:, [col for col in RESULT_COLUMNS if col in frame.columns]])
    if not frames:
        return pd.DataFrame(columns=RESULT_COLUMNS)
    return pd.concat(frames, ignore_index=True)
