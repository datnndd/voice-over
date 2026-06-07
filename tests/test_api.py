from __future__ import annotations

from fastapi.testclient import TestClient

from app.db import JobRepository
from app.main import app
from app.service import JobService
from app.worker import JobWorker


def test_job_api_create_get_cancel_and_outputs(tmp_path):
    repo = JobRepository(tmp_path / "jobs.db")
    worker = JobWorker(repo)
    app.state.service = JobService(repo, worker, tmp_path / "outputs")

    with TestClient(app) as client:
        response = client.post("/jobs", json={"type": "stt", "params": {"name": "test.mp4"}})
        assert response.status_code == 202
        job_id = response.json()["id"]

        detail = client.get(f"/jobs/{job_id}")
        assert detail.status_code == 200
        assert detail.json()["params"]["uuid"] == job_id

        outputs = client.get(f"/jobs/{job_id}/outputs")
        assert outputs.status_code == 200
        assert outputs.json()["job_id"] == job_id

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

