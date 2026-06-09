from typing import Union, List, Type

from app_core import ChannelProvider, get_class
from app_core.configure import contants
from app_core.configure.config import tr, params, app_cfg
from app_core.recognition._base import BaseRecogn
from app_core.task.taskcfg import SrtItem

QWENASR = 2
FUNASR_CN = 3
QWEN3ASR = 7
Deepgram = 10

ALLOW_CHANGE_MODEL = [QWENASR, FUNASR_CN, QWEN3ASR, Deepgram]

_ID_NAME_DICT = {
    QWENASR: ChannelProvider(f'Qwen-ASR({tr("Local")})', imp="._qwenasrlocal"),
    FUNASR_CN: ChannelProvider(tr("FunASR-Chinese"), imp="._funasr"),
    QWEN3ASR: ChannelProvider(tr("Ali Qwen3-ASR"), key_name="qwenmt_key", win="qwenmt", imp="._qwen3asr"),
    Deepgram: ChannelProvider("Deepgram.com", key_name="deepgram_apikey", win="deepgram", imp="._deepgram"),
}
_ID_NAME_DICT = dict(sorted(_ID_NAME_DICT.items(), key=lambda item: item[0]))
RECOGN_NAME_LIST = [it.name for it in _ID_NAME_DICT.values()]


def get_model_by_type(recogn_type: int) -> List[str]:
    if recogn_type == Deepgram:
        return contants.DEEPGRAM_MODEL
    if recogn_type == QWENASR:
        return ['1.7B', '0.6B']
    if recogn_type == FUNASR_CN:
        return contants.FUNASR_MODEL
    if recogn_type == QWEN3ASR:
        return ['qwen3-asr-flash']
    return []


def is_allow_lang(langcode: str = None, recogn_type: int = None, model_name=None):
    if recogn_type not in _ID_NAME_DICT:
        return f'Unsupported Recognition Channel:{recogn_type}'
    return True


def is_input_api(recogn_type: int = None, return_str=False):
    _cls = _ID_NAME_DICT.get(recogn_type)
    if not _cls:
        return f'Unsupported Recognition Channel:{recogn_type}'
    if _cls.key_name and not params.get(_cls.key_name):
        return f"Please configure the API Key information of the {_cls.name} channel first."
    return True


def run(*,
        detect_language=None,
        audio_file=None,
        cache_folder=None,
        model_name=None,
        uuid=None,
        recogn_type: int = QWENASR,
        is_cuda=None,
        subtitle_type=0,
        max_speakers=-1,
        llm_post=False,
        recogn2pass=False,
        punctuate=True
        ) -> Union[List[SrtItem], None]:
    if app_cfg.exit_soft or (uuid and uuid in app_cfg.stoped_uuid_set):
        return
    kwargs = {
        "detect_language": detect_language,
        "audio_file": audio_file,
        "cache_folder": cache_folder,
        "model_name": model_name,
        "uuid": uuid,
        "is_cuda": is_cuda,
        "subtitle_type": subtitle_type,
        "recogn_type": recogn_type,
        "max_speakers": max_speakers,
        "llm_post": llm_post,
        "recogn2pass": recogn2pass,
        "punctuate": punctuate,
    }
    _cls: Union[Type[BaseRecogn], None] = get_class(recogn_type, "recognition", _ID_NAME_DICT)
    if not _cls:
        raise RuntimeError(f'No this Recognition Channel:{recogn_type=}')

    return _cls(**kwargs).run()  # type:ignore