# voice-over

Backend-first voice-over API with owned `app_core` runtime.

## Phase 1 backend

Install dev dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Run API:

```powershell
python -m uvicorn app.main:app --reload
```

API contract for frontend work lives at `docs/API_CONTRACT.md`.

Useful endpoints:

- `POST /jobs`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/outputs`
- `POST /jobs/{job_id}/cancel`
- `GET /providers`

Run validation:

```powershell
python -m compileall -q app_core app tests scripts\smoke_api.py
python -m pytest -q
python scripts\smoke_api.py
```

Provider secrets must come from environment variables or local ignored config, never from tracked files.
`GET /providers` reports whether each provider is `local` or `api`, the neutral environment variable name to configure API providers, and whether that environment variable is currently set.


Provider visibility can be narrowed for MVP/runtime safety:

- `VOICE_OVER_PROVIDER_ALLOW=stt:0,tts:*` shows only matching provider tokens.
- `VOICE_OVER_PROVIDER_DENY=api` hides hosted API providers until secrets/runtime are configured.
- Supported tokens are `kind:id`, `kind:*`, `local`, `api`, and `*`.


Supported STT engines in `app_core` are intentionally trimmed to Deepgram, FunASR, and Qwen. Qwen keeps both local Qwen-ASR and API Qwen3-ASR variants; other STT modules were removed from the runtime registry and package.


Supported TTS engines in `app_core` are intentionally trimmed to Azure-TTS and OmniVoice local API. OmniVoice keeps the shared Gradio API helper used by the original project; other TTS engine modules were removed from the runtime package.


Supported LLM translation engines in `app_core` are intentionally trimmed to OpenAI ChatGPT and DeepSeek. Their original OpenAI-compatible helper is retained; other translator modules and LLM prompt files were removed from the runtime package.


Runtime launch checklist:

- Copy `.env.example` to `.env` and fill provider keys/URLs.
- Run `python scripts\smoke_real_video.py` to print dependency/config readiness and a real `video_translate` payload for `test.mp4`.
- Run `python scripts\smoke_real_video.py --run` only after all checks report `ready`.
- Check readiness through API with `GET /runtime/checks`.
