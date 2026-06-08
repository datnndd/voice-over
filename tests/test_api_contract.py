from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_openapi_exposes_stable_contract_schemas():
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    schemas = response.json()["components"]["schemas"]
    for schema_name in [
        "JobCreate",
        "JobParams",
        "JobRead",
        "JobDetail",
        "JobEventRead",
        "OutputFile",
        "OutputList",
        "ProviderInfo",
        "ProviderList",
        "RuntimeCheckRead",
    ]:
        assert schema_name in schemas

    output_props = schemas["OutputFile"]["properties"]
    assert set(output_props) == {"path", "filename", "extension", "kind", "size_bytes"}
    assert output_props["kind"]["enum"] == ["subtitle", "audio", "video", "other"]


def test_job_create_rejects_unknown_top_level_fields():
    with TestClient(app) as client:
        response = client.post("/jobs", json={"type": "stt", "params": {}, "unexpected": True})

    assert response.status_code == 422


def test_unknown_job_returns_contract_404():
    with TestClient(app) as client:
        response = client.get("/jobs/not-found")

    assert response.status_code == 404
    assert response.json() == {"detail": "job not found"}
