from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict

from app_core.configure import config

config.init_run()

from app_core.configure.config import app_cfg
from app_core.task.dubbing import DubbingSrt
from app_core.task.speech2text import SpeechToText
from app_core.task.taskcfg import TaskCfgSTS, TaskCfgSTT, TaskCfgTTS, TaskCfgVTT
from app_core.task.trans_create import TransCreate
from app_core.task.translate_srt import TranslateSrt


def _collect_outputs(target_dir: str | None) -> list[str]:
    if not target_dir:
        return []
    path = Path(target_dir)
    if not path.exists():
        return []
    return [item.as_posix() for item in path.rglob("*") if item.is_file()]


def _run_task(params: Dict[str, Any], task_factory: Callable[[Dict[str, Any]], Any], runner: Callable[[Any], None]) -> Dict[str, Any]:
    app_cfg.exit_soft = False
    app_cfg.exec_mode = "cli"
    task = None
    try:
        task = task_factory(dict(params))
        runner(task)
        target_dir = getattr(task.cfg, "target_dir", None)
        return {
            "status": "success",
            "target_dir": target_dir,
            "outputs": _collect_outputs(target_dir),
            "error": None,
        }
    except Exception as exc:
        target_dir = getattr(getattr(task, "cfg", None), "target_dir", params.get("target_dir"))
        return {
            "status": "error",
            "target_dir": target_dir,
            "outputs": _collect_outputs(target_dir),
            "error": str(exc),
        }


def run_stt(params: Dict[str, Any]) -> Dict[str, Any]:
    def factory(values: Dict[str, Any]) -> SpeechToText:
        return SpeechToText(cfg=TaskCfgSTT(**values), out_format="srt")

    def runner(task: SpeechToText) -> None:
        task.prepare()
        task.recogn()
        task.diariz()
        task.task_done()

    return _run_task(params, factory, runner)


def run_tts(params: Dict[str, Any]) -> Dict[str, Any]:
    def factory(values: Dict[str, Any]) -> DubbingSrt:
        return DubbingSrt(cfg=TaskCfgTTS(**values), out_ext="wav")

    def runner(task: DubbingSrt) -> None:
        task.prepare()
        task.dubbing()
        task.align()
        task.task_done()

    return _run_task(params, factory, runner)


def run_subtitle_translate(params: Dict[str, Any]) -> Dict[str, Any]:
    def factory(values: Dict[str, Any]) -> TranslateSrt:
        return TranslateSrt(cfg=TaskCfgSTS(**values), out_format=0)

    def runner(task: TranslateSrt) -> None:
        task.prepare()
        task.trans()
        task.task_done()

    return _run_task(params, factory, runner)


def run_video_translate(params: Dict[str, Any]) -> Dict[str, Any]:
    def factory(values: Dict[str, Any]) -> TransCreate:
        return TransCreate(cfg=TaskCfgVTT(**values))

    def runner(task: TransCreate) -> None:
        task.prepare()
        task.recogn()
        task.diariz()
        task.trans()
        task.dubbing()
        task.align()
        task.recogn2pass()
        task.assembling()
        task.task_done()

    return _run_task(params, factory, runner)
