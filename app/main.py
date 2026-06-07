from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.config import settings
from app.db import JobRepository
from app.models import JobCreate, JobDetail, JobRead, OutputList, ProviderList
from app.providers import list_providers
from app.service import JobService
from app.worker import JobWorker


def build_service() -> JobService:
    repository = JobRepository(settings.database_path)
    worker = JobWorker(repository)
    return JobService(repository, worker, settings.outputs_dir)


@asynccontextmanager
async def lifespan(api: FastAPI):
    service: JobService = api.state.service
    if settings.worker_enabled:
        service.worker.start()
    yield
    service.worker.stop()


app = FastAPI(title="Voice Over API", version="0.1.0", lifespan=lifespan)
app.state.service = build_service()


def get_service() -> JobService:
    return app.state.service


@app.post("/jobs", response_model=JobRead, status_code=202)
def create_job(request: JobCreate) -> JobRead:
    return get_service().create_job(request)


@app.get("/jobs/{job_id}", response_model=JobDetail)
def get_job(job_id: str) -> JobDetail:
    try:
        return get_service().get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc


@app.post("/jobs/{job_id}/cancel", response_model=JobRead)
def cancel_job(job_id: str) -> JobRead:
    try:
        return get_service().cancel_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc


@app.get("/jobs/{job_id}/outputs", response_model=OutputList)
def get_outputs(job_id: str) -> OutputList:
    try:
        return get_service().list_outputs(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="job not found") from exc


@app.get("/providers", response_model=ProviderList)
def providers() -> ProviderList:
    return list_providers()

