from pathlib import Path

from fastapi.testclient import TestClient

from storage_identification.reporting.app import create_app


def _client() -> TestClient:
    app = create_app(Path(__file__).parent / "fixtures" / "reporting")
    return TestClient(app)


def test_project_list_page_renders_demo_project():
    response = _client().get("/")

    assert response.status_code == 200
    assert "Demo Storage Report" in response.text


def test_project_overview_page_shows_kpis():
    response = _client().get("/projects/demo-project")

    assert response.status_code == 200
    assert "High-confidence storage enterprises" in response.text
    assert "Demo project summary" in response.text


def test_results_page_filters_by_tab_and_search():
    response = _client().get("/projects/demo-project/results?tab=high_confidence&q=1001")

    assert response.status_code == 200
    assert "1001" in response.text
    assert "1002" not in response.text


def test_enterprise_detail_page_shows_evidence():
    response = _client().get("/projects/demo-project/enterprises/1001")

    assert response.status_code == 200
    assert "Why This Enterprise Was Flagged" in response.text
    assert "M-100" in response.text


def test_methodology_page_renders():
    response = _client().get("/projects/demo-project/methodology")

    assert response.status_code == 200
    assert "How The Identification Works" in response.text


def test_create_app_without_fixture_root_uses_default_setting():
    app = create_app()

    assert app.title == "Storage Report Platform"
