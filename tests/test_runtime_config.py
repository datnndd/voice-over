from __future__ import annotations

from pathlib import Path

from app.runtime_config import apply_env_to_app_core, load_dotenv_file
from app.runtime_checks import check_provider
from app_core import recognition, translator, tts
from app_core.configure.config import params


def test_load_dotenv_file_sets_missing_env(monkeypatch, tmp_path):
    monkeypatch.delenv("VOICE_OVER_CHATGPT_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("VOICE_OVER_CHATGPT_KEY=sk-test\n", encoding="utf-8")

    values = load_dotenv_file(env_file)

    assert values["VOICE_OVER_CHATGPT_KEY"] == "sk-test"
    assert apply_env_to_app_core(["VOICE_OVER_CHATGPT_KEY"])["chatgpt_key"] == "sk-test"
    assert params["chatgpt_key"] == "sk-test"


def test_provider_check_reports_missing_required_config(monkeypatch):
    monkeypatch.setitem(params, "azure_speech_key", "")
    monkeypatch.setitem(params, "azure_speech_region", "")

    check = check_provider("tts", tts.AZURE_TTS, "Azure-TTS")

    assert check.status == "missing"
    assert "param:azure_speech_key" in check.missing
    assert "param:azure_speech_region" in check.missing


def test_provider_check_accepts_config_even_if_dependency_missing(monkeypatch):
    monkeypatch.setitem(params, "chatgpt_key", "sk-test")

    check = check_provider("translator", translator.CHATGPT_INDEX, "OpenAI ChatGPT")

    assert "param:chatgpt_key" not in check.missing


def test_selected_provider_ids_have_runtime_requirements():
    checks = [
        ("stt", recognition.Deepgram),
        ("stt", recognition.FUNASR_CN),
        ("stt", recognition.QWENASR),
        ("stt", recognition.QWEN3ASR),
        ("tts", tts.AZURE_TTS),
        ("tts", tts.OMNIVOICE_TTS),
        ("translator", translator.CHATGPT_INDEX),
        ("translator", translator.DEEPSEEK_INDEX),
    ]
    for kind, provider_id in checks:
        assert check_provider(kind, provider_id, f"{kind}:{provider_id}").provider_id == provider_id