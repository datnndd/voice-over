from __future__ import annotations

from typing import Any, Protocol

from app.models import JobType


class CoreFacade(Protocol):
    def run_stt(self, params: dict[str, Any]) -> dict[str, Any]: ...
    def run_tts(self, params: dict[str, Any]) -> dict[str, Any]: ...
    def run_subtitle_translate(self, params: dict[str, Any]) -> dict[str, Any]: ...
    def run_video_translate(self, params: dict[str, Any]) -> dict[str, Any]: ...


def run_core_job(job_type: JobType, params: dict[str, Any], facade: CoreFacade | None = None) -> dict[str, Any]:
    if facade is None:
        from web_core_reference import api as facade

    runners = {
        JobType.stt: facade.run_stt,
        JobType.tts: facade.run_tts,
        JobType.subtitle_translate: facade.run_subtitle_translate,
        JobType.video_translate: facade.run_video_translate,
    }
    return runners[job_type](params)

