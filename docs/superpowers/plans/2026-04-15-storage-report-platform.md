# Storage Report Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Railway-ready, reusable storage identification report platform that leads with project conclusions and supports enterprise-level evidence drill-down.

**Architecture:** Add a lightweight FastAPI application inside the existing Python repository. The app will read project-level report artifacts from a configurable data directory, transform them into a presentation-friendly model, and render a multi-page web experience with Jinja templates plus static CSS. Tests will cover project loading, summary derivation, and the key HTML routes.

**Tech Stack:** Python 3.13, FastAPI, Jinja2, Starlette TestClient, pandas, pytest, static CSS, vanilla JavaScript

---

### Task 1: Add Web App Dependencies And Data Fixtures

**Files:**
- Modify: `C:\Users\Pete\storage-identification\.worktrees\report-platform\pyproject.toml`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\tests\fixtures\reporting\demo-project\project.json`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\tests\fixtures\reporting\demo-project\enterprise_identification_base.csv`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\tests\fixtures\reporting\demo-project\enterprise_identification_high_confidence.csv`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\tests\fixtures\reporting\demo-project\enterprise_identification_manual_review.csv`
- Test: `C:\Users\Pete\storage-identification\.worktrees\report-platform\tests\test_report_data_loader.py`

- [ ] **Step 1: Write the failing loader test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_report_data_loader.py -q`
Expected: FAIL with `ModuleNotFoundError` for `storage_identification.reporting`

- [ ] **Step 3: Add app dependencies and minimal fixture files**

```toml
dependencies = [
  "numpy>=2.2.0",
  "pandas>=2.2.0",
  "pyarrow>=18.0.0",
  "fastapi>=0.115.0",
  "jinja2>=3.1.0",
  "uvicorn>=0.34.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.3.0",
  "httpx>=0.28.0",
]
```

```json
{
  "project_id": "demo-project",
  "project_name": "Demo Storage Report",
  "customer_name": "Demo Customer",
  "summary_text": "Demo project summary",
  "data_start_date": "2025-08-01",
  "data_end_date": "2025-10-31"
}
```

- [ ] **Step 4: Run the test to confirm it still fails for missing implementation**

Run: `python -m pytest tests/test_report_data_loader.py -q`
Expected: FAIL with missing `ReportRepository`

### Task 2: Implement The Project Data Layer

**Files:**
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\__init__.py`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\models.py`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\data_loader.py`
- Test: `C:\Users\Pete\storage-identification\.worktrees\report-platform\tests\test_report_data_loader.py`

- [ ] **Step 1: Implement minimal reporting models and loader**

```python
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
```

```python
class ReportRepository:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def list_projects(self) -> list[ReportProject]:
        ...
```

- [ ] **Step 2: Run the focused test**

Run: `python -m pytest tests/test_report_data_loader.py -q`
Expected: PASS

- [ ] **Step 3: Add one more failing test for enterprise detail loading**

```python
def test_report_repository_loads_enterprise_detail():
    fixture_root = Path(__file__).parent / "fixtures" / "reporting"
    repo = ReportRepository(fixture_root)

    detail = repo.get_enterprise_detail("demo-project", "1001")

    assert detail.enterprise.cons_no == "1001"
    assert detail.enterprise.business_label == "high_confidence_storage"
    assert detail.top_meters[0].made_no == "M-100"
```

- [ ] **Step 4: Implement the detail reader and rerun**

Run: `python -m pytest tests/test_report_data_loader.py -q`
Expected: PASS

### Task 3: Add The Web App Factory And Project Pages

**Files:**
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\app.py`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\settings.py`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\tests\test_report_routes.py`
- Test: `C:\Users\Pete\storage-identification\.worktrees\report-platform\tests\test_report_routes.py`

- [ ] **Step 1: Write the failing route test for the project list**

```python
from pathlib import Path

from fastapi.testclient import TestClient

from storage_identification.reporting.app import create_app


def test_project_list_page_renders_demo_project():
    app = create_app(Path(__file__).parent / "fixtures" / "reporting")
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Demo Storage Report" in response.text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_report_routes.py -q`
Expected: FAIL because `create_app` does not exist

- [ ] **Step 3: Implement minimal app factory and routes**

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse


def create_app(data_root: Path | None = None) -> FastAPI:
    app = FastAPI(title="Storage Report Platform")

    @app.get("/", response_class=HTMLResponse)
    def project_list(request: Request) -> HTMLResponse:
        ...

    return app
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_report_routes.py -q`
Expected: PASS

### Task 4: Build Jinja Templates And Static Styling

**Files:**
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\templates\base.html`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\templates\project_list.html`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\templates\project_overview.html`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\templates\results.html`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\templates\enterprise_detail.html`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\templates\methodology.html`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\static\report.css`
- Test: `C:\Users\Pete\storage-identification\.worktrees\report-platform\tests\test_report_routes.py`

- [ ] **Step 1: Add failing overview-page assertions**

```python
def test_project_overview_page_shows_kpis():
    app = create_app(Path(__file__).parent / "fixtures" / "reporting")
    client = TestClient(app)

    response = client.get("/projects/demo-project")

    assert response.status_code == 200
    assert "High-confidence storage enterprises" in response.text
    assert "1" in response.text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_report_routes.py -q`
Expected: FAIL because overview template is missing

- [ ] **Step 3: Implement the templates and CSS**

```html
<section class="hero">
  <p class="eyebrow">{{ project.customer_name or "Storage Identification" }}</p>
  <h1>{{ project.project_name }}</h1>
  <p>{{ project.summary_text }}</p>
</section>
```

```css
:root {
  --ink: #152238;
  --accent: #0f766e;
  --sand: #f5f0e8;
  --warn: #c2410c;
}
```

- [ ] **Step 4: Run the route tests**

Run: `python -m pytest tests/test_report_routes.py -q`
Expected: PASS

### Task 5: Add Results Filtering, Enterprise Detail Narrative, And Method Page

**Files:**
- Modify: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\data_loader.py`
- Modify: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\app.py`
- Modify: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\templates\results.html`
- Modify: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\templates\enterprise_detail.html`
- Modify: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\templates\methodology.html`
- Test: `C:\Users\Pete\storage-identification\.worktrees\report-platform\tests\test_report_routes.py`

- [ ] **Step 1: Add a failing filtering test**

```python
def test_results_page_filters_by_tab_and_search():
    app = create_app(Path(__file__).parent / "fixtures" / "reporting")
    client = TestClient(app)

    response = client.get("/projects/demo-project/results?tab=high_confidence&q=1001")

    assert response.status_code == 200
    assert "1001" in response.text
    assert "1002" not in response.text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_report_routes.py -q`
Expected: FAIL because filtering is not implemented

- [ ] **Step 3: Implement filtering and enterprise narrative blocks**

```python
def filter_enterprises(self, project_id: str, tab: str, query: str | None) -> list[EnterpriseRow]:
    ...
```

```html
<section class="narrative-card">
  <h2>Why This Enterprise Was Flagged</h2>
  <p>{{ detail.explanation }}</p>
</section>
```

- [ ] **Step 4: Run route tests**

Run: `python -m pytest tests/test_report_routes.py -q`
Expected: PASS

### Task 6: Add Runtime Entry Point And Full Verification

**Files:**
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\storage_identification\reporting\main.py`
- Create: `C:\Users\Pete\storage-identification\.worktrees\report-platform\README.md`
- Modify: `C:\Users\Pete\storage-identification\.worktrees\report-platform\pyproject.toml`
- Test: `C:\Users\Pete\storage-identification\.worktrees\report-platform\tests\test_report_data_loader.py`
- Test: `C:\Users\Pete\storage-identification\.worktrees\report-platform\tests\test_report_routes.py`
- Test: `C:\Users\Pete\storage-identification\.worktrees\report-platform\tests\test_cli_pipeline.py`

- [ ] **Step 1: Add a failing smoke test for app import**

```python
def test_create_app_without_fixture_root_uses_default_setting():
    app = create_app()
    assert app.title == "Storage Report Platform"
```

- [ ] **Step 2: Run focused tests**

Run: `python -m pytest tests/test_report_routes.py -q`
Expected: FAIL if default settings handling is missing

- [ ] **Step 3: Implement runtime entry point and README run instructions**

```python
from storage_identification.reporting.app import create_app

app = create_app()
```

```toml
[project.scripts]
storage-report = "storage_identification.reporting.main:run"
```

- [ ] **Step 4: Run full verification**

Run: `python -m pytest -q`
Expected: PASS with existing known warnings only

- [ ] **Step 5: Run manual app smoke command**

Run: `python -c "from storage_identification.reporting.app import create_app; app = create_app(); print(app.title)"`
Expected: print `Storage Report Platform`
