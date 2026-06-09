from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from app.config import ROOT_DIR

ENV_TO_PARAM = {
    "VOICE_OVER_DEEPGRAM_APIKEY": "deepgram_apikey",
    "VOICE_OVER_QWENMT_KEY": "qwenmt_key",
    "VOICE_OVER_QWEN3_ASR_MODEL": "qwenmt_asr_model",
    "VOICE_OVER_AZURE_SPEECH_KEY": "azure_speech_key",
    "VOICE_OVER_AZURE_SPEECH_REGION": "azure_speech_region",
    "VOICE_OVER_OMNIVOICE_URL": "omnivoice_url",
    "VOICE_OVER_VIENEU_MODE": "vieneu_mode",
    "VOICE_OVER_VIENEU_API_BASE": "vieneu_api_base",
    "VOICE_OVER_VIENEU_MODEL_NAME": "vieneu_model_name",
    "VOICE_OVER_VIENEU_VOICE_ROLES": "vieneu_voice_roles",
    "VOICE_OVER_CHATGPT_KEY": "chatgpt_key",
    "VOICE_OVER_CHATGPT_API": "chatgpt_api",
    "VOICE_OVER_CHATGPT_MODEL": "chatgpt_model",
    "VOICE_OVER_DEEPSEEK_KEY": "deepseek_key",
    "VOICE_OVER_DEEPSEEK_API": "deepseek_api",
    "VOICE_OVER_DEEPSEEK_MODEL": "deepseek_model",
}


def load_dotenv_file(path: Path | None = None) -> dict[str, str]:
    env_path = path or ROOT_DIR / ".env"
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
        values[key] = value
    return values


def apply_env_to_app_core(keys: Iterable[str] | None = None) -> dict[str, str]:
    from app_core.configure.config import params

    applied: dict[str, str] = {}
    selected_keys = set(keys) if keys else set(ENV_TO_PARAM)
    for env_key in selected_keys:
        param_key = ENV_TO_PARAM.get(env_key)
        value = os.getenv(env_key)
        if param_key and value:
            params[param_key] = value
            applied[param_key] = value
    return applied


def load_runtime_config() -> dict[str, str]:
    load_dotenv_file()
    return apply_env_to_app_core()
