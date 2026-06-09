from __future__ import annotations

from pathlib import Path

from app.config import DEFAULT_OUTPUTS_DIR, Settings


def test_default_processing_outputs_dir_is_downloads(monkeypatch):
    monkeypatch.delenv("VOICE_OVER_OUTPUTS", raising=False)

    settings = Settings()

    assert settings.outputs_dir == DEFAULT_OUTPUTS_DIR == Path(r"C:\Users\ddat2\Downloads")


def test_processing_outputs_dir_can_be_overridden(monkeypatch, tmp_path):
    monkeypatch.setenv("VOICE_OVER_OUTPUTS", tmp_path.as_posix())

    settings = Settings()

    assert settings.outputs_dir == tmp_path
