from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any
import re

from app.db import JobRepository
from app.models import JobCreate, JobDetail, JobRead, JobStatus, OutputList, UploadedMedia
from app.worker import JobWorker, drive_output_files, list_output_files

def safe_upload_filename(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    stem = Path(filename).stem or "upload"
    safe_stem = re.sub(r"[^a-zA-Z0-9_.-]+", "-", stem).strip(".-") or "upload"
    return f"{safe_stem}{suffix}"


def normalize_media_params(params: dict[str, Any], target_dir: Path) -> dict[str, Any]:
    normalized = dict(params)
    normalized.setdefault("target_dir", target_dir.as_posix())
    media_name = normalized.get("name")
    if not media_name:
        return normalized

    media_path = Path(media_name).expanduser().resolve()
    normalized["name"] = media_path.as_posix()
    normalized.setdefault("dirname", media_path.parent.as_posix())
    normalized.setdefault("basename", media_path.name)
    normalized.setdefault("noextname", media_path.stem or "output")
    normalized.setdefault("ext", media_path.suffix.lstrip("."))
    output_ext = normalized.get("ext") or "mp4"
    normalized.setdefault("targetdir_mp4", (target_dir / f"video_renew.{output_ext}").as_posix())
    return normalized


class JobService:
    def __init__(self, repository: JobRepository, worker: JobWorker, outputs_dir: Path, uploads_dir: Path | None = None) -> None:
        self.repository = repository
        self.worker = worker
        self.outputs_dir = outputs_dir
        self.uploads_dir = uploads_dir or outputs_dir / "uploads"
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)

    def create_job(self, request: JobCreate) -> JobRead:
        job_id = str(uuid.uuid4())
        target_dir = (self.outputs_dir / job_id).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        params = normalize_media_params(request.params.model_dump(exclude_none=True), target_dir)
        params.setdefault("uuid", job_id)
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
        local_outputs = list_output_files(job.get("target_dir"))
        if local_outputs:
            return OutputList(job_id=job_id, outputs=local_outputs)
        return OutputList(job_id=job_id, outputs=drive_output_files(self.repository.list_drive_outputs(job_id)))

    def save_uploaded_media(self, filename: str, content: bytes) -> UploadedMedia:
        if not content:
            raise ValueError("uploaded media is empty")
        upload_id = str(uuid.uuid4())
        target_dir = (self.uploads_dir / upload_id).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / safe_upload_filename(filename or "upload.mp4")
        target_path.write_bytes(content)
        return UploadedMedia(filename=target_path.name, path=target_path.as_posix(), size_bytes=target_path.stat().st_size)

