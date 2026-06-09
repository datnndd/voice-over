from __future__ import annotations

import sys
import types
from pathlib import Path

from app_core.tts._vieneu import VieNeuTTS


def test_vieneu_tts_uses_sdk_infer_and_save(tmp_path, monkeypatch):
    calls: dict[str, object] = {}

    class FakeVieneu:
        def __init__(self, **kwargs):
            calls["init"] = kwargs

        def infer(self, **kwargs):
            calls["infer"] = kwargs
            return b"audio"

        def save(self, audio, output):
            calls["save"] = {"audio": audio, "output": output}
            Path(output).write_bytes(b"wav")

        def close(self):
            calls["closed"] = True

    module = types.SimpleNamespace(Vieneu=FakeVieneu)
    monkeypatch.setitem(sys.modules, "vieneu", module)

    output = tmp_path / "line.wav"
    tts = VieNeuTTS(
        queue_tts=[{"text": "xin chao", "filename": output.as_posix(), "role": "Ngoc Lan"}],
        language="vi",
        uuid="test-vieneu",
        tts_type=32,
    )
    monkeypatch.setattr(tts, "convert_to_wav", lambda _source, target: Path(target).write_bytes(b"converted"))

    tts.run()

    assert output.read_bytes() == b"converted"
    assert calls["infer"] == {"text": "xin chao", "voice": "Ngoc Lan"}
    assert calls["closed"] is True
