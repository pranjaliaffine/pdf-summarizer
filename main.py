"""Optional FastAPI app exposing health and workflow run endpoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import get_settings
from run_workflow import run_workflow

app = FastAPI(title="PDF KYC Summarizer", version="1.0.0")


class RunRequest(BaseModel):
    pdf_path: str
    filename: str | None = None
    analyst_disposition: str | None = None
    analyst_notes: str | None = None
    dry_run: bool = False


class HealthResponse(BaseModel):
    status: str = "ok"
    agents_root: str
    manifest: str


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        agents_root=settings.agent_library_root,
        manifest=settings.workflow_manifest_path,
    )


@app.post("/run")
async def run_endpoint(request: RunRequest) -> dict[str, Any]:
    settings = get_settings()
    manifest_path = Path(settings.workflow_manifest_path)
    if not manifest_path.exists():
        raise HTTPException(status_code=500, detail="workflow manifest missing")

    pdf_path = Path(request.pdf_path)
    if not pdf_path.exists():
        raise HTTPException(status_code=400, detail=f"PDF not found: {pdf_path}")

    payload = {
        "pdf_path": str(pdf_path),
        "filename": request.filename or pdf_path.name,
    }
    if request.analyst_disposition:
        payload["analyst_disposition"] = request.analyst_disposition
    if request.analyst_notes:
        payload["analyst_notes"] = request.analyst_notes

    exit_code = await run_workflow(manifest_path, payload, dry_run=request.dry_run)
    if exit_code != 0:
        raise HTTPException(status_code=500, detail="Workflow execution failed")

    result_path = Path("output/workflow_result.json")
    return json.loads(result_path.read_text(encoding="utf-8"))
