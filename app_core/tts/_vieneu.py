import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Union

from tenacity import after_log, before_log, retry, retry_if_not_exception_type, stop_after_attempt, wait_fixed

from app_core.configure.config import logger, params, settings
from app_core.configure.excepts import NO_RETRY_EXCEPT, StopTask
from app_core.tts._base import BaseTTS


@dataclass
class VieNeuTTS(BaseTTS):
    _client: Any = field(default=None, init=False, repr=False)

    def _exec(self) -> None:
        try:
            for idx, item in enumerate(self.queue_tts, start=1):
                if self._exit():
                    return
                self.signal(text=f'Dubbing {idx}/{self.len}')
                error = self._item_task(item, idx)
                if error:
                    if isinstance(error, Exception):
                        raise error
                    raise RuntimeError(str(error))
                self.signal(text=f"TTS: [{idx}/{self.len}] ...")
            self.signal(text="TTS ended ...")
        finally:
            self._close_client()

    def _client_kwargs(self) -> dict[str, str]:
        kwargs: dict[str, str] = {}
        mode = str(params.get('vieneu_mode', '') or '').strip()
        api_base = str(params.get('vieneu_api_base', '') or '').strip()
        model_name = str(params.get('vieneu_model_name', '') or '').strip()
        if mode:
            kwargs['mode'] = mode
        if (mode or 'standard') == 'standard':
            local_model = self._cached_backbone_path()
            if local_model:
                kwargs['backbone_repo'] = local_model.as_posix()
        if api_base:
            kwargs['api_base'] = api_base
        if model_name:
            kwargs['model_name'] = model_name
        return kwargs

    def _cached_backbone_path(self) -> Path | None:
        cache_root = Path.home() / '.cache' / 'huggingface' / 'hub' / 'models--pnnbao-ump--VieNeu-TTS-v2' / 'snapshots'
        if not cache_root.exists():
            return None
        matches = sorted(cache_root.glob('*/VieNeu-TTS-v2-Q4-K-M.gguf'), key=lambda item: item.stat().st_mtime, reverse=True)
        return matches[0] if matches else None

    def _patch_standard_local_backbone(self) -> None:
        local_model = self._cached_backbone_path()
        if not local_model:
            return
        try:
            import vieneu.standard as standard
            from llama_cpp import Llama
        except Exception:
            return
        if getattr(standard.VieNeuTTS, '_voice_over_local_backbone_patch', False):
            return
        original = standard.VieNeuTTS._load_backbone

        def load_backbone(instance, backbone_repo: str, backbone_device: str, hf_token=None, gguf_filename=None):
            backbone_path = Path(backbone_repo)
            should_load_cached = (
                backbone_repo == 'pnnbao-ump/VieNeu-TTS-v2'
                and (gguf_filename or '').endswith('.gguf')
                and local_model.exists()
            )
            should_load_local_arg = backbone_path.exists() and backbone_path.suffix.lower() == '.gguf'
            if should_load_cached or should_load_local_arg:
                model_path = backbone_path if should_load_local_arg else local_model
                normalized_device = standard.normalize_device(backbone_device)
                logger.info(f'Loading cached VieNeu backbone from: {model_path} on {normalized_device} ...')
                instance.backbone = Llama(
                    model_path=model_path.as_posix(),
                    verbose=False,
                    n_gpu_layers=-1,
                    n_ctx=instance.max_context,
                    use_mlock=True,
                    flash_attn=True if normalized_device in ('gpu', 'cuda') else False,
                )
                instance._is_quantized_model = True
                return None
            return original(instance, backbone_repo, backbone_device, hf_token, gguf_filename)

        standard.VieNeuTTS._load_backbone = load_backbone
        standard.VieNeuTTS._voice_over_local_backbone_patch = True

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            self._patch_standard_local_backbone()
            from vieneu import Vieneu
        except ImportError as exc:
            raise StopTask('VieNeu-TTS dependency is missing. Install packages: pip install vieneu "llama-cpp-python>=0.3.16"') from exc
        self._client = Vieneu(**self._client_kwargs())
        return self._client

    def _close_client(self) -> None:
        client = self._client
        self._client = None
        if client and hasattr(client, 'close'):
            try:
                client.close()
            except Exception as exc:
                logger.warning(f'VieNeu-TTS close failed, skipped: {exc}')

    def _voice_kwargs(self, client, data_item: Dict[str, Any]) -> dict[str, Any]:
        role = str(data_item.get('role', '') or '').strip()
        if role == 'clone' or role in self.roledict:
            ref_wav, ref_text = self.get_ref_wav(data_item)
            kwargs: dict[str, Any] = {'ref_audio': ref_wav}
            if ref_text:
                kwargs['ref_text'] = ref_text
            return kwargs
        if role and role != 'No':
            if hasattr(client, 'get_preset_voice'):
                try:
                    return {'voice': client.get_preset_voice(role)}
                except Exception as exc:
                    available = client.list_preset_voices() if hasattr(client, 'list_preset_voices') else []
                    logger.warning(f'VieNeu preset voice not found: {role}. Available voices: {available}. Using default voice. Error: {exc}')
                    return {}
        return {}

    @retry(retry=retry_if_not_exception_type(NO_RETRY_EXCEPT), stop=(stop_after_attempt(settings.get('retry_nums'))), wait=wait_fixed(2), before=before_log(logger, logging.INFO), after=after_log(logger, logging.INFO))
    def _run(self, data_item: Union[Dict, List, None], idx: int = -1) -> Union[str, None]:
        if not isinstance(data_item, dict):
            return 'VieNeu-TTS data item must be a dict'
        client = self._get_client()
        output = data_item['filename'] + '-generate.wav'
        try:
            audio = client.infer(text=data_item.get('text', ''), **self._voice_kwargs(client, data_item))
        except TypeError:
            audio = client.infer(data_item.get('text', ''), **self._voice_kwargs(client, data_item))
        client.save(audio, output)
        if not Path(output).exists():
            return 'VieNeu-TTS did not create output audio'
        self.convert_to_wav(output, data_item['filename'])
        return None
