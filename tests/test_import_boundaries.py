from __future__ import annotations

from pathlib import Path


FORBIDDEN = ("web_core_reference", "videotrans")
CHECK_PATHS = [Path("app"), Path("app_core")]


def test_runtime_does_not_import_reference_packages():
    offenders: list[str] = []
    for root in CHECK_PATHS:
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for forbidden in FORBIDDEN:
                if forbidden in text:
                    offenders.append(f"{path}:{forbidden}")

    assert offenders == []