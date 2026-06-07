from __future__ import annotations

import importlib.util
import shutil
from dataclasses import dataclass

from app.runtime_config import load_runtime_config
from app_core import recognition, translator, tts
from app_core.configure.config import params


@dataclass(frozen=True)
class RuntimeCheck:
    provider_kind: str
    provider_id: int | None
    provider_name: str
    status: str
    missing: list[str]


PROVIDER_REQUIREMENTS = {
    ("stt", recognition.Deepgram): {
        "params": ["deepgram_apikey"],
        "modules": ["deepgram", "deepgram_captions", "httpx"],
    },
    ("stt", recognition.FUNASR_CN): {
        "params": [],
        "modules": ["funasr"],
    },
    ("stt", recognition.QWENASR): {
        "params": [],
        "modules": ["transformers"],
    },
    ("stt", recognition.QWEN3ASR): {
        "params": ["qwenmt_key"],
        "modules": ["dashscope"],
    },
    ("tts", tts.AZURE_TTS): {
        "params": ["azure_speech_key", "azure_speech_region"],
        "modules": ["azure.cognitiveservices.speech"],
    },
    ("tts", tts.OMNIVOICE_TTS): {
        "params": ["omnivoice_url"],
        "modules": ["gradio_client"],
    },
    ("translator", translator.CHATGPT_INDEX): {
        "params": ["chatgpt_key"],
        "modules": ["openai"],
    },
    ("translator", translator.DEEPSEEK_INDEX): {
        "params": ["deepseek_key"],
        "modules": ["openai"],
    },
}


def _module_missing(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is None
    except ModuleNotFoundError:
        return True


def check_provider(provider_kind: str, provider_id: int, provider_name: str) -> RuntimeCheck:
    requirements = PROVIDER_REQUIREMENTS.get((provider_kind, provider_id), {"params": [], "modules": []})
    missing: list[str] = []
    for param_key in requirements["params"]:
        if not params.get(param_key):
            missing.append(f"param:{param_key}")
    for module_name in requirements["modules"]:
        if _module_missing(module_name):
            missing.append(f"module:{module_name}")
    return RuntimeCheck(
        provider_kind=provider_kind,
        provider_id=provider_id,
        provider_name=provider_name,
        status="ready" if not missing else "missing",
        missing=missing,
    )


def check_runtime() -> list[RuntimeCheck]:
    load_runtime_config()
    checks: list[RuntimeCheck] = []
    for provider_id, provider in recognition._ID_NAME_DICT.items():
        checks.append(check_provider("stt", provider_id, provider.name))
    for provider_id, provider in tts._ID_NAME_DICT.items():
        checks.append(check_provider("tts", provider_id, provider.name))
    for provider_id, provider in translator._ID_NAME_DICT.items():
        checks.append(check_provider("translator", provider_id, provider.name))
    ffmpeg_missing = [] if shutil.which("ffmpeg") else ["binary:ffmpeg"]
    checks.append(RuntimeCheck("system", None, "ffmpeg", "ready" if not ffmpeg_missing else "missing", ffmpeg_missing))
    return checks