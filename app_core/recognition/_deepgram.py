import logging
import warnings
import os
import re
from dataclasses import dataclass
from typing import List, Union
from pathlib import Path
import json
import httpx
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)
from deepgram_captions import DeepgramConverter, srt
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_not_exception_type, before_log, after_log
from app_core.configure.excepts import NO_RETRY_EXCEPT, SpeechToTextError
from app_core.configure.config import tr,params,settings,logger
from app_core.recognition._base import BaseRecogn
from app_core.task.taskcfg import SrtItem
from app_core.util import tools
from app_core.configure import contants


_DEEPGRAM_NOVA3_GENERAL_LANGUAGES = {
    'ar', 'be', 'bn', 'bs', 'bg', 'ca', 'zh', 'hr', 'cs', 'da', 'nl', 'en', 'et', 'fi', 'fr', 'de', 'el', 'gu',
    'he', 'hi', 'hu', 'id', 'it', 'ja', 'kn', 'ko', 'lv', 'lt', 'mk', 'ms', 'mr', 'no', 'fa', 'pl', 'pt',
    'ro', 'ru', 'sr', 'sk', 'sl', 'es', 'sv', 'tl', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'vi',
}

_DEEPGRAM_NOVA3_MODELS = {'nova-3', 'nova-3-general'}
_DEEPGRAM_LEGACY_MODELS = {
    'nova-3-medical', 'nova-2', 'nova-2-general', 'enhanced', 'enhanced-general', 'base', 'base-general',
    'whisper-large', 'whisper-medium', 'whisper', 'whisper-small', 'whisper-base', 'whisper-tiny',
}


def _deepgram_model_name(model_name: str | None) -> str:
    normalized = (model_name or '').strip()
    if not normalized or normalized in _DEEPGRAM_LEGACY_MODELS:
        return 'nova-3'
    if normalized in _DEEPGRAM_NOVA3_MODELS:
        return normalized
    raise SpeechToTextError(f'Deepgram only supports nova-3 in this app, got model={normalized}')


def _validate_deepgram_language(model_name: str | None, language: str | None) -> None:
    if not language:
        return
    model = _deepgram_model_name(model_name)
    if language not in _DEEPGRAM_NOVA3_GENERAL_LANGUAGES:
        allowed_preview = ', '.join(sorted(_DEEPGRAM_NOVA3_GENERAL_LANGUAGES)[:24])
        raise SpeechToTextError(
            f'Deepgram model/language mismatch: model={model}, language={language}. '
            f'Choose one supported Nova 3 language. Examples: {allowed_preview}'
        )


def _deepgram_language_code(language: str | None) -> str | None:
    if not language:
        return language
    normalized = language.strip().replace('_', '-')
    if normalized.lower() == 'auto':
        return None
    return normalized[:2].lower()


def _deepgram_caption_line_length(language: str | None) -> int:
    lang = (language or '').lower()
    if lang[:2] in ['zh', 'ja', 'ko']:
        return int(settings.get('cjk_len'))
    return int(settings.get('other_len'))


def _deepgram_srt_from_response(response: object, language: str | None) -> str:
    transcription = DeepgramConverter(response)
    srt_text = srt(transcription, line_length=_deepgram_caption_line_length(language))
    if not srt_text or not srt_text.strip():
        raise SpeechToTextError('Deepgram returned an empty SRT caption result')
    return srt_text


def _deepgram_response_summary(response: object) -> dict[str, object]:
    try:
        if hasattr(response, 'get'):
            results = response.get('results', {})
        else:
            try:
                results = response['results']  # type: ignore[index]
            except Exception:
                results = getattr(response, 'results', {})
        channels = results.get('channels', []) if hasattr(results, 'get') else getattr(results, 'channels', [])
        utterances = results.get('utterances', []) if hasattr(results, 'get') else getattr(results, 'utterances', [])
        channel_count = len(channels or [])
        utterance_count = len(utterances or [])
        transcript_count = 0
        for channel in channels or []:
            alternatives = channel.get('alternatives', []) if hasattr(channel, 'get') else getattr(channel, 'alternatives', [])
            for alternative in alternatives or []:
                transcript = alternative.get('transcript', '') if hasattr(alternative, 'get') else getattr(alternative, 'transcript', '')
                if str(transcript).strip():
                    transcript_count += 1
        return {
            'channels': channel_count,
            'utterances': utterance_count,
            'non_empty_transcripts': transcript_count,
        }
    except Exception as exc:
        return {'summary_error': str(exc)}


@dataclass
class DeepgramRecogn(BaseRecogn):

    @retry(retry=retry_if_not_exception_type(NO_RETRY_EXCEPT), stop=(stop_after_attempt(settings.get('retry_nums'))), wait=wait_fixed(2), before=before_log(logger, logging.INFO),  after=after_log(logger, logging.INFO))
    def _exec(self) -> Union[List[SrtItem], None]:
        if self._exit(): return
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message='pkg_resources is deprecated as an API.*', category=UserWarning)
            import zhconv
        if os.path.getsize(self.audio_file) > 52428800:
            tools.runffmpeg(
                ['-y', '-i', self.audio_file, '-ac', '1', '-ar', '16000', self.cache_folder + '/deepgram-tmp.mp3'])
            self.audio_file = self.cache_folder + '/deepgram-tmp.mp3'
        with open(self.audio_file, "rb") as file:
            buffer_data = file.read()
        self.signal(
            text=tr("Recognition may take a while, please be patient"))

        httpx.HTTPTransport(proxy=self.proxy_str)

        deepgram = DeepgramClient(params.get('deepgram_apikey'))
        payload: FileSource = {
            "buffer": buffer_data,
        }

        diarize = self.max_speakers>-1
        model_name = _deepgram_model_name(self.model_name)
        language = _deepgram_language_code(self.detect_language)
        _validate_deepgram_language(model_name, language)
        self.signal(text=f'Deepgram request: model={model_name}, language={language or "auto-detect"}, diarize={diarize}')
        logger.info(f'Deepgram request: model={model_name}, language={language or "auto-detect"}, diarize={diarize}, audio={Path(self.audio_file).name}, bytes={len(buffer_data)}')
        options = PrerecordedOptions(
            model=model_name,
            detect_language=language is None,
            language=language,
            smart_format=True,
            punctuate=True,
            paragraphs=True,
            utterances=True,
            diarize=diarize,

            utt_split=int(settings.get('min_silence_duration_ms', 140)) / 1000,
        )

        res = deepgram.listen.rest.v("1").transcribe_file(payload, options, timeout=600)
        response_summary = _deepgram_response_summary(res)
        self.signal(text=f'Deepgram response: {json.dumps(response_summary, ensure_ascii=False)}')
        logger.info(f'Deepgram response summary: {response_summary}')

        raws = []
        if diarize:
            speaker_list=[]
            logger.debug(f"{res['results']['utterances']=}")
            for it in res['results']['utterances']:
                if not it.transcript.strip():
                    continue
                speaker_list.append(f'[spk{it.speaker}]')
                tmp = {
                    "line": len(raws) + 1,
                    "start_time": int(it.start * 1000),
                    "end_time": int(it.end * 1000),
                    "text": it.transcript
                }
                if self.detect_language[:2] in contants.CJK_LANG:
                    tmp['text'] = re.sub(r'\s| ', '', tmp['text'],flags=re.I | re.S)
                tmp['time'] = tools.ms_to_time_string(ms=tmp['start_time']) + ' --> ' + tools.ms_to_time_string(
                    ms=tmp['end_time'])
                raws.append(tmp)
            if speaker_list:
                Path(f'{self.cache_folder}/speaker.json').write_text(json.dumps(speaker_list), encoding='utf-8')
        else:
            try:
                srt_str = _deepgram_srt_from_response(res, self.detect_language)
            except Exception as exc:
                logger.warning(f'Deepgram SRT generation failed: {exc}; response_summary={response_summary}')
                self.signal(text=f'Deepgram SRT generation failed: {exc}; summary={json.dumps(response_summary, ensure_ascii=False)}', type='error')
                raise
            self.signal(text=f'Deepgram SRT generated: chars={len(srt_str)}')
            raws = tools.get_subtitle_from_srt(srt_str, is_file=False)
            if self.detect_language[:2] in contants.CJK_LANG:
                for i, it in enumerate(raws):
                    if self.detect_language[:2] == 'zh':
                        it['text'] = zhconv.convert(it['text'], 'zh-hans')
                    raws[i]['text'] = it['text'].replace(' ', '')

        self.signal(text=f'Deepgram subtitles parsed: lines={len(raws)}')
        logger.info(f'Deepgram subtitles parsed: lines={len(raws)}')

        return raws

