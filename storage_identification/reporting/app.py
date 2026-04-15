from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from storage_identification.reporting.data_loader import ReportRepository
from storage_identification.reporting.settings import (
    default_data_root,
    default_static_dir,
    default_template_dir,
)


def create_app(data_root: Path | None = None) -> FastAPI:
    repository = ReportRepository(data_root or default_data_root())
    templates = Jinja2Templates(directory=str(default_template_dir()))

    app = FastAPI(title="Storage Report Platform")
    app.mount("/static", StaticFiles(directory=str(default_static_dir())), name="static")

    @app.get("/", response_class=HTMLResponse)
    def project_list(request: Request) -> HTMLResponse:
        projects = repository.list_projects()
        return templates.TemplateResponse(
            request,
            "project_list.html",
            {
                "projects": projects,
                "page_title": "Storage Report Projects",
            },
        )

    @app.get("/projects/{project_id}", response_class=HTMLResponse)
    def project_overview(request: Request, project_id: str) -> HTMLResponse:
        project = repository.get_project(project_id)
        enterprises = repository.list_enterprises(project_id)
        high_confidence = [item for item in enterprises if item.business_label == "high_confidence_storage"][:5]
        review = [item for item in enterprises if item.business_label in {"storage_review", "uncertain_review"}][:5]
        return templates.TemplateResponse(
            request,
            "project_overview.html",
            {
                "project": project,
                "page_title": project.project_name,
                "high_confidence": high_confidence,
                "review": review,
            },
        )

    @app.get("/projects/{project_id}/results", response_class=HTMLResponse)
    def project_results(request: Request, project_id: str, tab: str = "all", q: str = "") -> HTMLResponse:
        project = repository.get_project(project_id)
        enterprises = _filter_enterprises(repository.list_enterprises(project_id), tab=tab, query=q)
        return templates.TemplateResponse(
            request,
            "results.html",
            {
                "project": project,
                "page_title": f"{project.project_name} Results",
                "enterprises": enterprises,
                "active_tab": tab,
                "query": q,
            },
        )

    @app.get("/projects/{project_id}/enterprises/{cons_no}", response_class=HTMLResponse)
    def enterprise_detail(request: Request, project_id: str, cons_no: str) -> HTMLResponse:
        try:
            detail = repository.get_enterprise_detail(project_id, cons_no)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return templates.TemplateResponse(
            request,
            "enterprise_detail.html",
            {
                "detail": detail,
                "project": detail.project,
                "page_title": f"{detail.enterprise.cons_no} Detail",
            },
        )

    @app.get("/projects/{project_id}/methodology", response_class=HTMLResponse)
    def methodology(request: Request, project_id: str) -> HTMLResponse:
        project = repository.get_project(project_id)
        return templates.TemplateResponse(
            request,
            "methodology.html",
            {
                "project": project,
                "page_title": f"{project.project_name} Methodology",
            },
        )

    return app


def _filter_enterprises(enterprises, tab: str, query: str):
    query_text = query.strip()
    filtered = enterprises
    if tab == "high_confidence":
        filtered = [item for item in filtered if item.business_label == "high_confidence_storage"]
    elif tab == "review":
        filtered = [item for item in filtered if item.business_label in {"storage_review", "uncertain_review"}]
    if query_text:
        filtered = [item for item in filtered if query_text in item.cons_no]
    return filtered
