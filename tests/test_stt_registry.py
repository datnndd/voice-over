from __future__ import annotations

from pathlib import Path

from app_core import recognition
from app_core.configure.excepts import SpeechToTextError
from app_core.recognition import _deepgram


def test_stt_registry_only_keeps_deepgram_funasr_qwen_family():
    assert set(recognition._ID_NAME_DICT) == {
        recognition.QWENASR,
        recognition.FUNASR_CN,
        recognition.QWEN3ASR,
        recognition.Deepgram,
    }
    names = " ".join(provider.name for provider in recognition._ID_NAME_DICT.values()).lower()
    assert "deepgram" in names
    assert "funasr" in names
    assert "qwen" in names
    forbidden = ["whisper", "google", "gemini", "eleven", "huggingface", "camb"]
    assert all(item not in names for item in forbidden)


def test_removed_stt_modules_are_not_present():
    remaining = {path.name for path in Path("app_core/recognition").glob("*.py")}
    assert remaining == {
        "__init__.py",
        "_base.py",
        "_deepgram.py",
        "_funasr.py",
        "_qwen3asr.py",
        "_qwenasrlocal.py",
    }


def test_deepgram_caption_line_length_uses_cjk_settings():
    assert _deepgram._deepgram_caption_line_length("zh-HK") == int(_deepgram.settings.get("cjk_len"))
    assert _deepgram._deepgram_caption_line_length("ja") == int(_deepgram.settings.get("cjk_len"))
    assert _deepgram._deepgram_caption_line_length("en") == int(_deepgram.settings.get("other_len"))


def test_deepgram_srt_helper_rejects_empty_caption(monkeypatch):
    monkeypatch.setattr(_deepgram, "DeepgramConverter", lambda response: response)
    monkeypatch.setattr(_deepgram, "srt", lambda transcription, line_length: "")

    try:
        _deepgram._deepgram_srt_from_response(object(), "en")
    except SpeechToTextError as exc:
        assert "empty SRT" in str(exc)
    else:
        raise AssertionError("empty Deepgram caption should fail")
