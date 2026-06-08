# voice-over

Backend-first voice-over API with owned `app_core` runtime.


## Quick Start

Use Python 3.11 venv for local AI providers. Python 3.14 can fail on some AI wheels.

```powershell
uv venv --python 3.11 .venv
uv pip install --python .venv\Scripts\python.exe -e ".[dev,providers,local-ai]"
```

Copy env file and fill provider values you use:

```powershell
Copy-Item .env.example .env
```

Run backend in terminal 1:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Run frontend in terminal 2:

```powershell
cd frontend
npm install
npm run dev
```

Open frontend:

```text
http://127.0.0.1:5173
```

If frontend shows `Failed to fetch`, backend is probably not running on `http://127.0.0.1:8000`.

Override frontend API URL if needed:

```powershell
$env:VITE_API_BASE_URL="http://127.0.0.1:8000"
cd frontend
npm run dev
```

## Common Commands

Backend validation:

```powershell
.\.venv\Scripts\python.exe scripts\validate_phase1.py
```

Frontend validation:

```powershell
cd frontend
npm run lint
npm run build
```

Real video smoke test:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_real_video.py
.\.venv\Scripts\python.exe scripts\smoke_real_video.py --run
```

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
