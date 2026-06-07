from __future__ import annotations

from dataclasses import replace

from fastapi.testclient import TestClient

from app import providers
from app.config import settings
from app.main import app


def test_providers_endpoint_exposes_runtime_and_env_shape():
    with TestClient(app) as client:
        response = client.get("/providers")

    assert response.status_code == 200
    payload = response.json()
    all_providers = payload["stt"] + payload["tts"] + payload["translators"]
    assert all_providers
    assert {"runtime", "env_var", "configured", "config_mode"}.issubset(all_providers[0].keys())
    assert any(provider["runtime"] == "local" for provider in all_providers)
    assert any(provider["runtime"] == "api" and provider["env_var"] for provider in all_providers)


def test_provider_allow_filter_limits_runtime(monkeypatch):
    monkeypatch.setattr(providers, "settings", replace(settings, provider_allow=frozenset({"stt:2"}), provider_deny=frozenset()))

    payload = providers.list_providers()

    assert [provider.id for provider in payload.stt] == [2]
    assert payload.tts == []
    assert payload.translators == []


def test_provider_deny_filter_removes_api_providers(monkeypatch):
    monkeypatch.setattr(providers, "settings", replace(settings, provider_allow=frozenset(), provider_deny=frozenset({"api"})))

    payload = providers.list_providers()
    all_providers = payload.stt + payload.tts + payload.translators

    assert all_providers
    assert {provider.runtime for provider in all_providers} == {"local"}