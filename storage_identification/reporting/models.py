from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReportProject:
    project_id: str
    project_name: str
    customer_name: str | None
    summary_text: str
    data_start_date: str
    data_end_date: str
    enterprise_total: int
    high_confidence_total: int
    manual_review_total: int
    no_storage_total: int


@dataclass(slots=True)
class EnterpriseRecord:
    cons_no: str
    delivery_bucket: str
    business_label: str
    cons_storage_label: str
    cons_storage_score: float
    review_priority: int
    review_reason: str
    meter_count: int
    active_meter_count: int
    positive_meter_count: int
    strong_positive_meter_count: int
    has_storage_meter_count: int
    uncertain_meter_count: int
    no_storage_meter_count: int
    pair_rule_hit_count_top5: int
    none_rule_hit_count_top5: int
    top_meter_list: list[str]
    top_evidence_days: list[str]
    top_hit_rules: list[str]


@dataclass(slots=True)
class MeterEvidence:
    rank: int
    made_no: str
    label: str
    score: float
    usable_day_count: int
    positive_day_ratio: float
    strong_positive_day_count: int
    weak_positive_day_count: int
    evidence_days: list[str]
    hit_rules: list[str]


@dataclass(slots=True)
class EnterpriseDetail:
    project: ReportProject
    enterprise: EnterpriseRecord
    top_meters: list[MeterEvidence]
    explanation: str

