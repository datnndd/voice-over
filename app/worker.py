from __future__ import annotations

import queue
import threading
from pathlib import Path
from typing import Any

from app.core_facade import CoreFacade, run_core_job
from app.db import JobRepository
from app.models import JobStatus, JobType


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
        self.repository.update_status(job_id, JobStatus.running)
        self.repository.add_event(job_id, "logs", "job started")
        try:
            result = run_core_job(JobType(job["type"]), job["params"], self.facade)
            target_dir = result.get("target_dir") or job.get("target_dir")
            if self.repository.get_job(job_id)["status"] == JobStatus.canceled.value:
                self.repository.add_event(job_id, "stop", "job canceled")
                return self.repository.get_job(job_id)
            if result.get("status") == "success":
                self.repository.add_event(job_id, "succeed", "job succeeded")
                return self.repository.update_status(job_id, JobStatus.succeeded, target_dir=target_dir)
            error = result.get("error") or "core job failed"
            self.repository.add_event(job_id, "error", error)
            return self.repository.update_status(job_id, JobStatus.failed, error=error, target_dir=target_dir)
        except Exception as exc:
            self.repository.add_event(job_id, "error", str(exc))
            return self.repository.update_status(job_id, JobStatus.failed, error=str(exc))

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
            event_type = getattr(data, "type", "logs") or "logs"
            text = getattr(data, "text", "") if data is not None else ""
            self.repository.add_event(uuid, str(event_type), str(text))

        SignalHub.instance().new_message.connect(_record_event)


def list_output_files(target_dir: str | None) -> list[str]:
    if not target_dir:
        return []
    path = Path(target_dir)
    if not path.exists():
        return []
    return [item.as_posix() for item in path.rglob("*") if item.is_file()]