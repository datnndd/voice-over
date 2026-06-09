from __future__ import annotations

from pathlib import Path

from app_core import tts


def test_tts_registry_keeps_supported_tts_providers():
    assert set(tts._ID_NAME_DICT) == {tts.OMNIVOICE_TTS, tts.AZURE_TTS, tts.VIENEU_TTS}
    names = " ".join(provider.name for provider in tts._ID_NAME_DICT.values()).lower()
    assert "azure" in names
    assert "omnivoice" in names
    assert "vieneu" in names
    forbidden = ["edge", "openai", "qwen", "eleven", "gemini", "camb", "piper", "kokoro"]
    assert all(item not in names for item in forbidden)


def test_removed_tts_modules_are_not_present():
    remaining = {path.name for path in Path("app_core/tts").glob("*.py")}
    assert remaining == {
        "__init__.py",
        "_base.py",
        "_azuretts.py",
        "_omnivoice.py",
        "_vieneu.py",
        "_gradio.py",
    }
