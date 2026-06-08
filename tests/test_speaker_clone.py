from __future__ import annotations

import json
from pathlib import Path

from app_core.task.speaker_clone import build_speaker_references


def test_build_speaker_references_groups_lines_by_speaker(monkeypatch, tmp_path):
    audio = tmp_path / "source.wav"
    audio.write_bytes(b"audio")
    speaker_file = tmp_path / "speaker.json"
    speaker_file.write_text(json.dumps(["[spk0]", "[spk1]", "[spk0]"]), encoding="utf-8")
    source_subs = [
        {"line": 1, "start_time": 0, "end_time": 6000, "startraw": "00:00:00,000", "endraw": "00:00:06,000", "text": "hello one"},
        {"line": 2, "start_time": 6000, "end_time": 12000, "startraw": "00:00:06,000", "endraw": "00:00:12,000", "text": "hello two"},
        {"line": 3, "start_time": 12000, "end_time": 18000, "startraw": "00:00:12,000", "endraw": "00:00:18,000", "text": "hello three"},
    ]

    def fake_cut_from_audio(*, audio_file, ss, to, out_file):
        Path(out_file).write_bytes(f"{ss}->{to}".encode())
        return True

    def fake_runffmpeg(args, **kwargs):
        Path(args[-1]).write_bytes(b"joined")
        return True

    monkeypatch.setattr("app_core.task.speaker_clone.tools.cut_from_audio", fake_cut_from_audio)
    monkeypatch.setattr("app_core.task.speaker_clone.tools.runffmpeg", fake_runffmpeg)

    refs = build_speaker_references(
        audio_file=audio.as_posix(),
        source_subs=source_subs,
        speaker_file=speaker_file.as_posix(),
        output_dir=tmp_path.as_posix(),
        min_seconds=10,
        max_seconds=15,
    )

    assert set(refs) == {"spk0", "spk1"}
    assert refs["spk0"].ref_text == "hello one hello three"
    assert refs["spk1"].ref_text == "hello two"
    assert Path(refs["spk0"].ref_wav).exists()
    speakers_json = tmp_path / "speaker_refs" / "speakers.json"
    assert speakers_json.exists()
