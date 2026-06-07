_STT_EXPORTS = {"openai_whisper", "faster_whisper", "pipe_asr", "paraformer", "funasr_mlt", "qwen3asr_fun"}
_TTS_EXPORTS = {"qwen3tts_fun"}


def __getattr__(name):
    if name in _STT_EXPORTS:
        from web_core_reference.process import stt_fun
        return getattr(stt_fun, name)
    if name in _TTS_EXPORTS:
        from web_core_reference.process import tts_fun
        return getattr(tts_fun, name)
    raise AttributeError(name)


__all__ = sorted(_STT_EXPORTS | _TTS_EXPORTS)
