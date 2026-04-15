# Storage Report Platform

This repository now includes a reusable web report layer for storage identification projects.

## What It Does

The report platform provides:

1. A project list page
2. A conclusion-first project overview page
3. A results page for enterprise review
4. An enterprise detail page with supporting meter evidence
5. A methodology page explaining the identification logic

## Local Run

Install dependencies:

```powershell
python -m pip install fastapi jinja2 uvicorn httpx
```

Run the app with the project script:

```powershell
storage-report
```

Or run Uvicorn directly:

```powershell
python -m uvicorn storage_identification.reporting.main:app --host 0.0.0.0 --port 8000
```

Railway can also use the repository root entrypoint:

```powershell
python main.py
```

The default data source is the bundled demo project under `storage_identification/reporting/demo_data`.

To point the app at real project data, set:

```powershell
$env:STORAGE_REPORT_DATA_DIR="C:\path\to\report-projects"
```

The configured directory should contain one subdirectory per project, and each project directory should include:

1. `project.json`
2. `enterprise_identification_base.csv`

## Railway Direction

For Railway deployment, run the app with Uvicorn against:

`storage_identification.reporting.main:app`
