from __future__ import annotations

from fastapi.testclient import TestClient

from app.db import JobRepository
from app.main import app
from app.models import JobType
from app.service import JobService
from app.service import normalize_media_params
from app.worker import JobWorker


def test_job_api_create_get_cancel_and_outputs(tmp_path):
    repo = JobRepository(tmp_path / "jobs.db")
    worker = JobWorker(repo)
    app.state.service = JobService(repo, worker, tmp_path / "outputs")

    with TestClient(app) as client:
        response = client.post("/jobs", json={"type": "video_translate", "params": {"name": "test.mp4"}})
        assert response.status_code == 202
        job_id = response.json()["id"]

        detail = client.get(f"/jobs/{job_id}")
        assert detail.status_code == 200
        params = detail.json()["params"]
        assert params["uuid"] == job_id
        assert params["basename"] == "test.mp4"
        assert params["noextname"] == "test"
        assert params["ext"] == "mp4"
        assert params["targetdir_mp4"].endswith("/video_renew.mp4")
        assert not params["targetdir_mp4"].endswith("/None.mp4")

        outputs = client.get(f"/jobs/{job_id}/outputs")
        assert outputs.status_code == 200
        output_payload = outputs.json()
        assert output_payload["job_id"] == job_id
        assert output_payload["outputs"] == []

        canceled = client.post(f"/jobs/{job_id}/cancel")
        assert canceled.status_code == 200
        assert canceled.json()["status"] == "canceled"


def test_providers_endpoint_returns_registry():
    with TestClient(app) as client:
        response = client.get("/providers")

    assert response.status_code == 200
    payload = response.json()
    assert "stt" in payload
    assert "tts" in payload
    assert "translators" in payload

def test_tts_job_normalizes_srt_input_without_video_output(tmp_path):
    srt_path = tmp_path / "line.srt"
    srt_path.write_text("1\n00:00:00,000 --> 00:00:01,000\nhello\n", encoding="utf-8")
    target_dir = tmp_path / "outputs"

    params = normalize_media_params({"name": srt_path.as_posix(), "tts_type": 28}, target_dir, JobType.tts)

    assert params["name"] == srt_path.resolve().as_posix()
    assert params["target_dir"] == target_dir.as_posix()
    assert params["cache_folder"] == (target_dir / "cache").as_posix()
    assert params["noextname"] == "line"
    assert params["ext"] == "srt"
    assert "targetdir_mp4" not in params

