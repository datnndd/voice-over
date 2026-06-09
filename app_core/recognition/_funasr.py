import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List,  Union
from app_core.configure import config
from app_core.process import paraformer, funasr_mlt
from app_core.recognition._base import BaseRecogn
from app_core.task.taskcfg import SrtItem
from app_core.util import tools


def _funasr_language_code(language: str | None) -> str:
    if not language or language.lower() == 'auto':
        return 'auto'
    normalized = language.strip().lower().replace('_', '-')
    if normalized in {'zh-hk', 'zh-mo', 'yue-hk', 'cantonese'}:
        return 'yue'
    if normalized in {'zh-cn', 'zh-hans', 'zh-tw', 'zh-hant', 'mandarin'}:
        return 'zh'
    return normalized.split('-')[0]


@dataclass
class FunasrRecogn(BaseRecogn):

    def _exec(self) -> Union[List[SrtItem], None]:
        if self._exit():
            return
        if self.punctuate:
            tools.check_and_down_ms(model_id='damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch',callback=self._process_callback)
        detect_language = _funasr_language_code(self.detect_language)

        if self.model_name == 'paraformer-zh' and detect_language not in ['zh', 'en']:
            self.model_name = 'FunAudioLLM/Fun-ASR-MLT-Nano-2512' if detect_language not in ['zh','en','ja','yue'] else 'FunAudioLLM/Fun-ASR-Nano-2512'
            tools.check_and_down_ms(model_id=self.model_name,callback=self._process_callback)
        elif self.model_name == 'SenseVoiceSmall':
            self.model_name = 'iic/SenseVoiceSmall'
        elif self.model_name == 'Fun-ASR-Nano-2512':
            if detect_language not in ['zh', 'en', 'ja', 'yue']:
                self.model_name = f'FunAudioLLM/Fun-ASR-MLT-Nano-2512'
            else:
                self.model_name = f'FunAudioLLM/Fun-ASR-Nano-2512'
        elif self.model_name != 'paraformer-zh':
            self.model_name = f'FunAudioLLM/Fun-ASR-MLT-Nano-2512'

        if self.model_name == 'paraformer-zh':
            tools.check_and_down_ms(model_id='iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch',callback=self._process_callback)
            tools.check_and_down_ms(model_id='damo/speech_fsmn_vad_zh-cn-16k-common-pytorch',callback=self._process_callback)
            if self.punctuate:
                tools.check_and_down_ms(model_id='damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch',callback=self._process_callback)
            tools.check_and_down_ms(model_id='damo/speech_campplus_sv_zh-cn_16k-common',callback=self._process_callback)
        else:
            tools.check_and_down_ms(model_id=self.model_name,callback=self._process_callback)
        self.signal(text=f"load {self.model_name}")
        logs_file = f'{config.TEMP_DIR}/{self.uuid}/funasr-{detect_language}-{time.time()}.log'
        if self.model_name != 'paraformer-zh':
            cut_audio_list_file = f'{config.TEMP_DIR}/{self.uuid}/cut_audio_list_{time.time()}.json'
            Path(cut_audio_list_file).write_text( json.dumps( [ asdict(item) for item in self.cut_audio() ] ),encoding='utf-8')
        else:
            cut_audio_list_file=None
        kwars = {
            "cut_audio_list":   cut_audio_list_file,
            "detect_language": detect_language,
            "model_name": self.model_name,
            "logs_file": logs_file,
            "is_cuda": self.is_cuda,
            "audio_file": self.audio_file,
            "max_speakers": self.max_speakers,
            "cache_folder": self.cache_folder,
            "punctuate": self.punctuate
        }
        raws=self._new_process(callback=paraformer if self.model_name == 'paraformer-zh' else funasr_mlt,title=f'STT use {self.model_name}',is_cuda=self.is_cuda,kwargs=kwars)
        return raws

