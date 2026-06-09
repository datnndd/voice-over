from __future__ import annotations

import queue
import re
import shutil
import threading
from pathlib import Path
from typing import Any

from app.config import settings
from app.core_facade import CoreFacade, run_core_job
from app.db import JobRepository
from app.drive import GoogleDriveUploader
from app.models import JobStatus, JobType, OutputFile


def _progress_from_event(event_type: str, text: str) -> int | None:
    normalized_type = event_type.lower()
    normalized_text = text.lower()
    percent_match = re.search(r"(?<!\d)(\d{1,3})(?:\.\d+)?\s*%", text)
    if percent_match:
        return max(0, min(99, int(percent_match.group(1))))
    if normalized_type in {"succeed", "end"}:
        return 100
    if normalized_type == "error":
        return None
    phase_markers = (
        ("starting", 8),
        ("load", 12),
        ("recognition", 20),
        ("subtitle", 35),
        ("translat", 55),
        ("tts", 70),
        ("compose", 88),
        ("merge", 90),
        ("output", 95),
    )
    for marker, progress in phase_markers:
        if marker in normalized_text:
            return progress
    return None


class JobWorker:
    def __init__(self, repository: JobRepository, facade: CoreFacade | None = None) -> None:
        self.repository = repository
        self.facade = facade
        self._queue: queue.Queue[str] = queue.Queue()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._connect_signal_hub()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run_loop, name="voice-over-worker", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._queue.put("")
        if self._thread:
            self._thread.join(timeout=5)

    def enqueue(self, job_id: str) -> None:
        self._queue.put(job_id)

    def run_once(self, job_id: str) -> dict[str, Any]:
        job = self.repository.get_job(job_id)
        if job["status"] == JobStatus.canceled.value:
            return job
        self.repository.update_status(job_id, JobStatus.running, progress_percent=5)
        self.repository.add_event(job_id, "logs", "job started")
        try:
            result = run_core_job(JobType(job["type"]), job["params"], self.facade)
            target_dir = result.get("target_dir") or job.get("target_dir")
            if self.repository.get_job(job_id)["status"] == JobStatus.canceled.value:
                self.repository.add_event(job_id, "stop", "job canceled")
                return self.repository.get_job(job_id)
            if result.get("status") == "success":
                self._upload_outputs_and_cleanup(job_id, target_dir, job["params"])
                self.repository.add_event(job_id, "succeed", "job succeeded")
                return self.repository.update_status(job_id, JobStatus.succeeded, target_dir=target_dir, progress_percent=100)
            error = result.get("error") or "core job failed"
            self.repository.add_event(job_id, "error", error)
            return self.repository.update_status(job_id, JobStatus.failed, error=error, target_dir=target_dir)
        except Exception as exc:
            self.repository.add_event(job_id, "error", str(exc))
            return self.repository.update_status(job_id, JobStatus.failed, error=str(exc))

    def _upload_outputs_and_cleanup(self, job_id: str, target_dir: str | None, params: dict[str, Any]) -> None:
        if not settings.google_drive_enabled:
            return
        outputs = list_output_files(target_dir)
        if not outputs:
            self.repository.add_event(job_id, "drive", "no local outputs to upload")
            return
        self.repository.add_event(job_id, "drive", f"uploading {len(outputs)} output file(s) to Google Drive")
        uploader = GoogleDriveUploader(
            credentials_file=settings.google_drive_credentials_file,
            credentials_json=settings.google_drive_credentials_json,
            folder_id=settings.google_drive_folder_id,
        )
        uploaded = uploader.upload_outputs(outputs)
        for result in uploaded:
            self.repository.add_drive_output(job_id, result.to_record())
        self.repository.add_event(job_id, "drive", f"uploaded {len(uploaded)} output file(s) to Google Drive")
        self._cleanup_local_files(job_id, target_dir, params)

    def _cleanup_local_files(self, job_id: str, target_dir: str | None, params: dict[str, Any]) -> None:
        target_path = Path(target_dir).resolve() if target_dir else None
        if target_path and target_path.exists():
            shutil.rmtree(target_path)
            self.repository.add_event(job_id, "cleanup", f"deleted local output directory: {target_path.as_posix()}")
        input_path = Path(str(params.get("name") or "")).resolve()
        uploads_root = settings.uploads_dir.resolve()
        if input_path and input_path.exists() and input_path.is_file() and input_path.is_relative_to(uploads_root):
            input_path.unlink()
            self.repository.add_event(job_id, "cleanup", f"deleted uploaded input file: {input_path.as_posix()}")

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            job_id = self._queue.get()
            if not job_id:
                continue
            self.run_once(job_id)

    def _connect_signal_hub(self) -> None:
        try:
            from app_core.configure.signal_hub import SignalHub
        except Exception:
            return

        def _record_event(uuid: str, data: object) -> None:
            if not uuid:
                return
            try:
                self.repository.get_job(uuid)
            except KeyError:
                return
            event_type = str(getattr(data, "type", "logs") or "logs")
            text = str(getattr(data, "text", "") if data is not None else "")
            self.repository.add_event(uuid, event_type, text)
            progress = getattr(data, "percent", None) if data is not None else None
            if progress is None:
                progress = _progress_from_event(event_type, text)
            if progress is not None:
                self.repository.update_progress(uuid, int(float(progress)))

        SignalHub.instance().new_message.connect(_record_event)


def _output_kind(extension: str) -> str:
    normalized = extension.lower()
    if normalized in {".srt", ".vtt", ".ass"}:
        return "subtitle"
    if normalized in {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}:
        return "audio"
    if normalized in {".mp4", ".mov", ".mkv", ".webm"}:
        return "video"
    return "other"

def list_output_files(target_dir: str | None) -> list[OutputFile]:
    if not target_dir:
        return []
    path = Path(target_dir)
    if not path.exists():
        return []
    outputs: list[OutputFile] = []
    for item in path.rglob("*"):
        if not item.is_file():
            continue
        extension = item.suffix.lower()
        outputs.append(
            OutputFile(
                path=item.as_posix(),
                filename=item.name,
                extension=extension,
                kind=_output_kind(extension),
                size_bytes=item.stat().st_size,
                storage="local",
            )
        )
    return outputs

def drive_output_files(records: list[dict[str, Any]]) -> list[OutputFile]:
    return [
        OutputFile(
            path=str(record["drive_web_view_link"] or record["local_path"]),
            filename=str(record["filename"]),
            extension=str(record["extension"]),
            kind=record["kind"],
            size_bytes=int(record["size_bytes"]),
            storage="google_drive",
            drive_file_id=str(record["drive_file_id"]),
            drive_web_view_link=record.get("drive_web_view_link"),
        )
        for record in records
    ]
