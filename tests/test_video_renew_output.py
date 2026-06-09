from __future__ import annotations

from pathlib import Path

from app_core.task.taskcfg import TaskCfgVTT
from app_core.task.trans_create import TransCreate


def test_video_translate_prepare_copies_video_without_novoice_split(tmp_path, monkeypatch):
    source_video = tmp_path / "source.mp4"
    source_video.write_bytes(b"video bytes")
    target_dir = tmp_path / "outputs"

    cfg = TaskCfgVTT(
        uuid="job-1",
        name=source_video.as_posix(),
        dirname=tmp_path.as_posix(),
        basename=source_video.name,
        noextname=source_video.stem,
        ext="mp4",
        target_dir=target_dir.as_posix(),
        cache_folder=(tmp_path / "cache").as_posix(),
        source_language_code="en",
        target_language_code="vi",
        detect_language="en",
        voice_role="TestVoice",
    )

    monkeypatch.setattr(
        "app_core.task.trans_create.tools.get_video_info",
        lambda _name: {
            "video_streams": 1,
            "streams_audio": 1,
            "video_codec_name": "h264",
            "audio_codec_name": "aac",
            "color": "yuv420p",
            "time": 1000,
        },
    )

    def fail_novoice_split(_callback):
        raise AssertionError("novoice split should not run")

    monkeypatch.setattr("app_core.task.trans_create.run_in_threadpool", fail_novoice_split)

    def write_source_wav(self, is_separate=False):
        Path(self.cfg.source_wav).write_bytes(b"audio bytes")

    monkeypatch.setattr(TransCreate, "_split_audio_byraw", write_source_wav)

    task = TransCreate(cfg=cfg)
    task.prepare()

    video_renew = target_dir / "video_renew.mp4"
    assert video_renew.read_bytes() == source_video.read_bytes()
    assert task.cfg.targetdir_mp4 == video_renew.as_posix()
    assert not Path(task.cfg.novoice_mp4).exists()
