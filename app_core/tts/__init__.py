from typing import Union, Type

from app_core import ChannelProvider, get_class
from app_core.configure.config import tr, params, app_cfg
from app_core.configure.excepts import DubbingSrtError
from app_core.tts._base import BaseTTS

EDGE_TTS = 0
QWEN3LOCAL_TTS = 1
OMNIVOICE_TTS = 2
MOSS_TTS = 3
PIPER_TTS = 4
VITSCNEN_TTS = 5
Supertonic_TTS = 6
CHATTERBOX_TTS = 7
F5_TTS = 8
INDEX_TTS = 9
GPTSOVITS_TTS = 10
COSYVOICE_TTS = 11
VOXCPM_TTS = 12
DOUBAO2_TTS = 13
QWEN_TTS = 14
XIAOMI_TTS = 15
GLM_TTS = 16
MINIMAXI_TTS = 17
OPENAI_TTS = 18
GEMINI_TTS = 19
ELEVENLABS_TTS = 20
XAI_TTS = 21
CHATTTS = 22
SPARK_TTS = 23
DIA_TTS = 24
KOKORO_TTS = 25
CLONE_VOICE_TTS = 26
FISHTTS = 27
AZURE_TTS = 28
AI302_TTS = 29
CAMB_TTS = 30
TTS_API = 31
VIENEU_TTS = 32

SUPPORT_CLONE = [OMNIVOICE_TTS, VIENEU_TTS]
CHANGE_BY_LANGUAGE = [AZURE_TTS]

_ID_NAME_DICT = {
    OMNIVOICE_TTS: ChannelProvider(f"OmniVoice({tr('Local')}API)", "._omnivoice", key_name="omnivoice_url", win="omnivoice"),
    AZURE_TTS: ChannelProvider("Azure-TTS", "._azuretts", key_name="azure_speech_key", win="azuretts"),
    VIENEU_TTS: ChannelProvider("VieNeu-TTS", "._vieneu", win="vieneu"),
}
_ID_NAME_DICT = dict(sorted(_ID_NAME_DICT.items(), key=lambda item: item[0]))
TTS_NAME_LIST = [it.name for it in _ID_NAME_DICT.values()]


def is_allow_lang(tts_type: int = 0, lang: str = None) -> bool:
    return tts_type in _ID_NAME_DICT


def is_input_api(tts_type: int = 0, return_str=False):
    _cls = _ID_NAME_DICT.get(tts_type)
    if not _cls:
        return f'Unsupported TTS Channel:{tts_type}'
    if _cls.key_name and not params.get(_cls.key_name):
        return f"Please configure the API information of the {_cls.name} channel first."
    return True


def clone_tips(tts_type, role: str = 'No', recogn_type=9):
    if tts_type in SUPPORT_CLONE and role == 'clone':
        return tr('Please select a valid role')
    return True


def run(*, queue_tts=None, language=None, uuid=None, play=False, is_test=False, tts_type=AZURE_TTS, is_cuda=False) -> None:
    if len(queue_tts) < 1 or app_cfg.exit_soft or (uuid and uuid in app_cfg.stoped_uuid_set):
        return
    kwargs = {
        "queue_tts": queue_tts,
        "language": language,
        "uuid": uuid,
        "play": play,
        "is_test": is_test,
        "tts_type": tts_type,
        "is_cuda": is_cuda,
    }

    _cls: Union[Type[BaseTTS], None] = get_class(tts_type, "tts", _ID_NAME_DICT)
    if not _cls:
        raise DubbingSrtError(f'No this TTS Channel:{tts_type=}')

    return _cls(**kwargs).run()  # type:ignore
