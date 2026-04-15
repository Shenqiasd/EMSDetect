from __future__ import annotations

import uvicorn

from storage_identification.reporting.app import create_app

app = create_app()


def run() -> None:
    uvicorn.run(
        "storage_identification.reporting.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
