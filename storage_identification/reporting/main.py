from __future__ import annotations

import os

import uvicorn

from storage_identification.reporting.app import create_app

app = create_app()


def run() -> None:
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "storage_identification.reporting.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )
