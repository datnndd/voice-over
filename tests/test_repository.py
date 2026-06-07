from __future__ import annotations

from app.db import JobRepository
from app.models import JobStatus, JobType


def test_repository_create_update_and_events(tmp_path):
    repo = JobRepository(tmp_path / "jobs.db")
    job = repo.create_job("job-1", JobType.stt, {"name": "input.wav"}, (tmp_path / "out").as_posix())

    assert job["id"] == "job-1"
    assert job["status"] == JobStatus.queued.value
    assert job["params"] == {"name": "input.wav"}

    repo.add_event("job-1", "logs", "queued")
    updated = repo.update_status("job-1", JobStatus.running)

    assert updated["status"] == JobStatus.running.value
    assert repo.list_events("job-1")[0]["text"] == "queued"

