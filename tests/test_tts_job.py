from __future__ import annotations

from pathlib import Path

from app_core import api


def test_run_tts_ignores_video_only_fields(monkeypatch, tmp_path):
    captured = {}

    class FakeDubbingSrt:
        def __init__(self, cfg, out_ext):
            captured["cfg"] = cfg
            self.cfg = cfg

        def prepare(self):
            pass

        def dubbing(self):
            Path(self.cfg.target_dir).mkdir(parents=True, exist_ok=True)
            Path(self.cfg.target_dir, "line.wav").write_bytes(b"RIFF")

        def align(self):
            pass

        def task_done(self):
            pass

    monkeypatch.setattr(api, "DubbingSrt", FakeDubbingSrt)

    result = api.run_tts(
        {
            "name": (tmp_path / "line.srt").as_posix(),
            "target_dir": (tmp_path / "outputs").as_posix(),
            "cache_folder": (tmp_path / "cache").as_posix(),
            "noextname": "line",
            "tts_type": 28,
            "voice_role": "HoaiMy(Female)",
            "target_language_code": "vi",
            "subtitle_language": "vi",
            "app_mode": "peiyin",
        }
    )

    assert result["status"] == "success"
    assert captured["cfg"].tts_type == 28
    assert not hasattr(captured["cfg"], "subtitle_language")
    assert not hasattr(captured["cfg"], "app_mode")
