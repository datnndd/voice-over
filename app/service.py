from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from app.db import JobRepository
from app.models import JobCreate, JobDetail, JobRead, JobStatus, OutputList
from app.worker import JobWorker, list_output_files


class JobService:
    def __init__(self, repository: JobRepository, worker: JobWorker, outputs_dir: Path) -> None:
        self.repository = repository
        self.worker = worker
        self.outputs_dir = outputs_dir
        self.outputs_dir.mkdir(parents=True, exist_ok=True)

    def create_job(self, request: JobCreate) -> JobRead:
        job_id = str(uuid.uuid4())
        target_dir = (self.outputs_dir / job_id).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        params: dict[str, Any] = dict(request.params)
        params.setdefault("uuid", job_id)
        params.setdefault("target_dir", target_dir.as_posix())
        job = self.repository.create_job(job_id, request.type, params, target_dir.as_posix())
        self.repository.add_event(job_id, "logs", "job queued")
        self.worker.enqueue(job_id)
        return JobRead.model_validate(job)

    def get_job(self, job_id: str) -> JobDetail:
        job = self.repository.get_job(job_id)
        events = self.repository.list_events(job_id)
        return JobDetail.model_validate(job | {"events": events})

    def cancel_job(self, job_id: str) -> JobRead:
        from app_core.configure.config import app_cfg

        app_cfg.stoped_uuid_set.add(job_id)
        self.repository.add_event(job_id, "stop", "job canceled")
        job = self.repository.update_status(job_id, JobStatus.canceled)
        return JobRead.model_validate(job)

    def list_outputs(self, job_id: str) -> OutputList:
        job = self.repository.get_job(job_id)
        return OutputList(job_id=job_id, outputs=list_output_files(job.get("target_dir")))

