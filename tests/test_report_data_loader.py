from pathlib import Path

from storage_identification.reporting.data_loader import ReportRepository


def test_report_repository_loads_project_summary():
    fixture_root = Path(__file__).parent / "fixtures" / "reporting"
    repo = ReportRepository(fixture_root)

    projects = repo.list_projects()

    assert len(projects) == 1
    project = projects[0]
    assert project.project_id == "demo-project"
    assert project.enterprise_total == 3
    assert project.high_confidence_total == 1
    assert project.manual_review_total == 1


def test_report_repository_loads_enterprise_detail():
    fixture_root = Path(__file__).parent / "fixtures" / "reporting"
    repo = ReportRepository(fixture_root)

    detail = repo.get_enterprise_detail("demo-project", "1001")

    assert detail.enterprise.cons_no == "1001"
    assert detail.enterprise.business_label == "high_confidence_storage"
    assert detail.top_meters[0].made_no == "M-100"
