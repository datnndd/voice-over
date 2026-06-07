from __future__ import annotations

from dataclasses import dataclass

from app.config import parse_csv_env
from app_core.providers import ProviderKind, ProviderRuntime, descriptor_from_legacy, env_var_for_key, is_configured


@dataclass
class LegacyProvider:
    name: str
    key_name: str | None = None


def test_env_var_for_legacy_key_name():
    assert env_var_for_key("gemini_key") == "VOICE_OVER_GEMINI_KEY"
    assert env_var_for_key("trans-api url") == "VOICE_OVER_TRANS_API_URL"
    assert env_var_for_key(None) is None


def test_parse_csv_env_normalizes_tokens(monkeypatch):
    monkeypatch.setenv("VOICE_OVER_PROVIDER_ALLOW", " stt:0, API ,tts:* ")
    assert parse_csv_env("VOICE_OVER_PROVIDER_ALLOW") == frozenset({"stt:0", "api", "tts:*"})


def test_descriptor_marks_local_provider_when_no_key():
    descriptor = descriptor_from_legacy(ProviderKind.stt, 0, LegacyProvider("Local Whisper"))

    assert descriptor.runtime == ProviderRuntime.local
    assert descriptor.config_mode == "local"
    assert descriptor.env_var is None
    assert is_configured(descriptor) is True


def test_descriptor_marks_api_provider_and_reads_env(monkeypatch):
    descriptor = descriptor_from_legacy(ProviderKind.translator, 1, LegacyProvider("Gemini", "gemini_key"))

    assert descriptor.runtime == ProviderRuntime.api
    assert descriptor.config_mode == "env"
    assert descriptor.env_var == "VOICE_OVER_GEMINI_KEY"
    assert is_configured(descriptor) is False

    monkeypatch.setenv("VOICE_OVER_GEMINI_KEY", "secret")
    assert is_configured(descriptor) is True