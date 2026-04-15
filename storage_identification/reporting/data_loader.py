from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd

from storage_identification.reporting.models import (
    EnterpriseDetail,
    EnterpriseRecord,
    MeterEvidence,
    ReportProject,
)


DELIVERY_BUCKET_TO_BUSINESS_LABEL = {
    "A_high_confidence_storage": "high_confidence_storage",
    "B_storage_review": "storage_review",
    "C_uncertain_review": "uncertain_review",
    "D_no_storage": "no_storage",
}


def _split_pipe(text: str | float | int | None) -> list[str]:
    if text is None:
        return []
    if isinstance(text, float) and pd.isna(text):
        return []
    raw = str(text).strip()
    if not raw:
        return []
    return [part for part in raw.split("|") if part]


def _safe_int(value: object) -> int:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0
    return int(float(value))


def _safe_float(value: object) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0.0
    return float(value)


class ReportRepository:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def list_projects(self) -> list[ReportProject]:
        projects = [self._load_project(project_dir) for project_dir in sorted(self.root.iterdir()) if project_dir.is_dir()]
        return sorted(projects, key=lambda item: item.project_name.lower())

    def get_project(self, project_id: str) -> ReportProject:
        return self._load_project(self.root / project_id)

    def list_enterprises(self, project_id: str) -> list[EnterpriseRecord]:
        df = self._load_base_frame(project_id)
        return [self._to_enterprise_record(row) for _, row in df.iterrows()]

    def get_enterprise_detail(self, project_id: str, cons_no: str) -> EnterpriseDetail:
        project = self.get_project(project_id)
        df = self._load_base_frame(project_id)
        matches = df[df["CONS_NO"] == cons_no]
        if matches.empty:
            raise KeyError(f"Enterprise {cons_no} not found in project {project_id}")

        row = matches.iloc[0]
        enterprise = self._to_enterprise_record(row)
        top_meters = self._build_top_meters(row)
        explanation = self._build_explanation(enterprise, top_meters)
        return EnterpriseDetail(
            project=project,
            enterprise=enterprise,
            top_meters=top_meters,
            explanation=explanation,
        )

    @lru_cache(maxsize=32)
    def _load_project(self, project_dir: Path) -> ReportProject:
        metadata = json.loads((project_dir / "project.json").read_text(encoding="utf-8"))
        base_df = self._load_base_frame(metadata["project_id"])

        enterprise_total = len(base_df)
        high_confidence_total = int((base_df["delivery_bucket"] == "A_high_confidence_storage").sum())
        manual_review_total = int(base_df["delivery_bucket"].isin(["B_storage_review", "C_uncertain_review"]).sum())
        no_storage_total = int((base_df["delivery_bucket"] == "D_no_storage").sum())

        return ReportProject(
            project_id=metadata["project_id"],
            project_name=metadata["project_name"],
            customer_name=metadata.get("customer_name"),
            summary_text=metadata["summary_text"],
            data_start_date=metadata["data_start_date"],
            data_end_date=metadata["data_end_date"],
            enterprise_total=enterprise_total,
            high_confidence_total=high_confidence_total,
            manual_review_total=manual_review_total,
            no_storage_total=no_storage_total,
        )

    @lru_cache(maxsize=32)
    def _load_base_frame(self, project_id: str) -> pd.DataFrame:
        project_dir = self.root / project_id
        df = pd.read_csv(project_dir / "enterprise_identification_base.csv", dtype={"CONS_NO": "string"})
        df["CONS_NO"] = df["CONS_NO"].fillna("")
        return df

    def _to_enterprise_record(self, row: pd.Series) -> EnterpriseRecord:
        delivery_bucket = str(row.get("delivery_bucket", "")).strip()
        return EnterpriseRecord(
            cons_no=str(row["CONS_NO"]),
            delivery_bucket=delivery_bucket,
            business_label=DELIVERY_BUCKET_TO_BUSINESS_LABEL.get(delivery_bucket, "no_storage"),
            cons_storage_label=str(row.get("cons_storage_label", "")),
            cons_storage_score=_safe_float(row.get("cons_storage_score")),
            review_priority=_safe_int(row.get("review_priority")),
            review_reason=str(row.get("review_reason", "")),
            meter_count=_safe_int(row.get("meter_count")),
            active_meter_count=_safe_int(row.get("active_meter_count")),
            positive_meter_count=_safe_int(row.get("positive_meter_count")),
            strong_positive_meter_count=_safe_int(row.get("strong_positive_meter_count")),
            has_storage_meter_count=_safe_int(row.get("has_storage_meter_count")),
            uncertain_meter_count=_safe_int(row.get("uncertain_meter_count")),
            no_storage_meter_count=_safe_int(row.get("no_storage_meter_count")),
            pair_rule_hit_count_top5=_safe_int(row.get("pair_rule_hit_count_top5")),
            none_rule_hit_count_top5=_safe_int(row.get("none_rule_hit_count_top5")),
            top_meter_list=_split_pipe(row.get("top_meter_list")),
            top_evidence_days=_split_pipe(row.get("top_evidence_days")),
            top_hit_rules=_split_pipe(row.get("top_hit_rules")),
        )

    def _build_top_meters(self, row: pd.Series) -> list[MeterEvidence]:
        meters: list[MeterEvidence] = []
        for rank in (1, 2, 3):
            made_no = str(row.get(f"top{rank}_made_no", "")).strip()
            if not made_no or made_no == "nan":
                continue
            meters.append(
                MeterEvidence(
                    rank=rank,
                    made_no=made_no,
                    label=str(row.get(f"top{rank}_meter_label", "")),
                    score=_safe_float(row.get(f"top{rank}_meter_score")),
                    usable_day_count=_safe_int(row.get(f"top{rank}_usable_day_count")),
                    positive_day_ratio=_safe_float(row.get(f"top{rank}_positive_day_ratio")),
                    strong_positive_day_count=_safe_int(row.get(f"top{rank}_strong_positive_day_count")),
                    weak_positive_day_count=_safe_int(row.get(f"top{rank}_weak_positive_day_count")),
                    evidence_days=_split_pipe(row.get(f"top{rank}_meter_evidence_days")),
                    hit_rules=_split_pipe(row.get(f"top{rank}_meter_hit_rules")),
                )
            )
        return meters

    def _build_explanation(self, enterprise: EnterpriseRecord, top_meters: list[MeterEvidence]) -> str:
        lead_meter = top_meters[0].made_no if top_meters else "the lead meter"
        if enterprise.business_label == "high_confidence_storage":
            return (
                f"Enterprise {enterprise.cons_no} is high-confidence storage because meter {lead_meter} "
                f"shows repeated charge/discharge evidence with {enterprise.strong_positive_meter_count} strong-signal meters."
            )
        if enterprise.business_label in {"storage_review", "uncertain_review"}:
            return (
                f"Enterprise {enterprise.cons_no} should be reviewed because meter {lead_meter} "
                f"shows partial storage evidence across {enterprise.positive_meter_count} positive-signal meters."
            )
        return f"Enterprise {enterprise.cons_no} does not currently show sustained storage evidence."
