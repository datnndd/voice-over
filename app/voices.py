from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from app.models import CloneVoiceRef, VoiceInfo, VoiceList
from app_core import tts
from app_core.configure.config import ROOT_DIR, params
from app_core.util import tools


def _gender_from_name(name: str) -> str | None:
    lowered = name.lower()
    if 'female' in lowered:
        return 'female'
    if 'male' in lowered:
        return 'male'
    return None


@lru_cache(maxsize=128)
def list_voices(tts_type: int, language: str | None = None) -> VoiceList:
    language_code = (language or '').strip().lower() or None
    names = tools.role_menu(tts_type, language_code)
    voices = [
        VoiceInfo(
            name=str(name),
            value=str(name),
            language=language_code,
            gender=_gender_from_name(str(name)),
        )
        for name in names
    ]
    return VoiceList(tts_type=tts_type, language=language_code, voices=voices)


def default_voice_for(tts_type: int, language: str | None = None) -> str:
    voice_list = list_voices(tts_type, language)
    if tts_type == tts.AZURE_TTS and language and language.lower().startswith('vi'):
        for voice in voice_list.voices:
            if voice.name == 'HoaiMy(Female)':
                return voice.name
    for voice in voice_list.voices:
        if voice.name != 'No':
            return voice.name
    return 'No'


def _safe_clone_name(filename: str) -> str:
    stem = Path(filename).stem or 'clone'
    suffix = Path(filename).suffix.lower() or '.wav'
    safe_stem = re.sub(r'[^a-zA-Z0-9_.-]+', '-', stem).strip('.-') or 'clone'
    return f'{safe_stem}{suffix}'


def save_clone_reference(filename: str, content: bytes, ref_text: str) -> CloneVoiceRef:
    if not content:
        raise ValueError('clone reference audio is empty')
    if not ref_text.strip():
        raise ValueError('clone reference text is required')
    safe_name = _safe_clone_name(filename)
    target_dir = Path(ROOT_DIR) / 'f5-tts'
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / safe_name
    target_path.write_bytes(content)

    existing = str(params.get('f5tts_role', '') or '').strip()
    rows = [row for row in existing.splitlines() if row.strip() and not row.strip().startswith(f'{safe_name}#')]
    rows.append(f'{safe_name}#{ref_text.strip()}')
    params['f5tts_role'] = '\n'.join(rows)
    list_voices.cache_clear()
    return CloneVoiceRef(name=safe_name, path=target_path.as_posix(), ref_text=ref_text.strip())
