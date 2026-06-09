from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from app.db import JobRepository
from app.models import JobStatus, JobType
from app.service import JobService
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
    outputs = list_output_files(target_dir.as_posix())

    assert len(outputs) == 1
    assert outputs[0].path == (target_dir / "result.srt").as_posix()
    assert outputs[0].filename == "result.srt"
    assert outputs[0].extension == ".srt"
    assert outputs[0].kind == "subtitle"
    assert outputs[0].size_bytes > 0

class FakeDriveUploader:
    def __init__(self, **_kwargs):
        pass

    def upload_outputs(self, outputs):
        return [
            SimpleNamespace(
                to_record=lambda output=output: {
                    "local_path": output.path,
                    "filename": output.filename,
                    "extension": output.extension,
                    "kind": output.kind,
                    "size_bytes": output.size_bytes,
                    "drive_file_id": f"drive-{output.filename}",
                    "drive_web_view_link": f"https://drive.example/{output.filename}",
                }
            )
            for output in outputs
        ]

def test_worker_uploads_outputs_to_drive_and_cleans_local_files(tmp_path, monkeypatch):
    repo = JobRepository(tmp_path / "jobs.db")
    outputs_dir = tmp_path / "outputs"
    target_dir = outputs_dir / "job-1"
    target_dir.mkdir(parents=True)
    uploads_dir = tmp_path / "uploads"
    input_dir = uploads_dir / "upload-1"
    input_dir.mkdir(parents=True)
    input_file = input_dir / "input.mp4"
    input_file.write_bytes(b"input")
    repo.create_job("job-1", JobType.stt, {"target_dir": target_dir.as_posix(), "name": input_file.as_posix()}, target_dir.as_posix())
    monkeypatch.setattr("app.worker.settings", SimpleNamespace(
        google_drive_enabled=True,
        google_drive_credentials_file=None,
        google_drive_credentials_json="{}",
        google_drive_folder_id="folder",
        uploads_dir=uploads_dir,
    ))
    monkeypatch.setattr("app.worker.GoogleDriveUploader", FakeDriveUploader)

    worker = JobWorker(repo, FakeFacade())
    job = worker.run_once("job-1")

    assert job["status"] == JobStatus.succeeded.value
    assert not target_dir.exists()
    assert not input_file.exists()
    records = repo.list_drive_outputs("job-1")
    assert records[0]["drive_file_id"] == "drive-result.srt"
    output_list = JobService(repo, worker, outputs_dir, uploads_dir).list_outputs("job-1")
    assert output_list.outputs[0].storage == "google_drive"
    assert output_list.outputs[0].drive_web_view_link == "https://drive.example/result.srt"

def test_worker_keeps_local_files_when_drive_upload_fails(tmp_path, monkeypatch):
    class FailingDriveUploader:
        def __init__(self, **_kwargs):
            pass

        def upload_outputs(self, _outputs):
            raise RuntimeError("drive unavailable")

    repo = JobRepository(tmp_path / "jobs.db")
    target_dir = tmp_path / "outputs"
    target_dir.mkdir()
    repo.create_job("job-1", JobType.stt, {"target_dir": target_dir.as_posix()}, target_dir.as_posix())
    monkeypatch.setattr("app.worker.settings", SimpleNamespace(
        google_drive_enabled=True,
        google_drive_credentials_file=None,
        google_drive_credentials_json="{}",
        google_drive_folder_id="folder",
        uploads_dir=tmp_path / "uploads",
    ))
    monkeypatch.setattr("app.worker.GoogleDriveUploader", FailingDriveUploader)

    worker = JobWorker(repo, FakeFacade())
    job = worker.run_once("job-1")

    assert job["status"] == JobStatus.failed.value
    assert target_dir.exists()
    assert (target_dir / "result.srt").exists()

