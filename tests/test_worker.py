from __future__ import annotations

from pathlib import Path

from app.db import JobRepository
from app.models import JobStatus, JobType
from app.worker import JobWorker, list_output_files


class FakeFacade:
    def run_stt(self, params):
        output = Path(params["target_dir"]) / "result.srt"
        output.write_text("1\n00:00:00,000 --> 00:00:01,000\nhello\n", encoding="utf-8")
        return {"status": "success", "target_dir": params["target_dir"], "outputs": [output.as_posix()], "error": None}

    def run_tts(self, params):
        return self.run_stt(params)

    def run_subtitle_translate(self, params):
        return self.run_stt(params)

    def run_video_translate(self, params):
        return self.run_stt(params)


def test_worker_runs_facade_and_records_outputs(tmp_path):
    repo = JobRepository(tmp_path / "jobs.db")
    target_dir = tmp_path / "outputs"
    target_dir.mkdir()
    repo.create_job("job-1", JobType.stt, {"target_dir": target_dir.as_posix()}, target_dir.as_posix())

    worker = JobWorker(repo, FakeFacade())
    job = worker.run_once("job-1")

    assert job["status"] == JobStatus.succeeded.value
    assert list_output_files(target_dir.as_posix()) == [(target_dir / "result.srt").as_posix()]

