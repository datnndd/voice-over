# voice-over

Backend-first voice-over API around `web_core_reference`.

## Phase 1 backend

Install dev dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Run API:

```powershell
python -m uvicorn app.main:app --reload
```

Useful endpoints:

- `POST /jobs`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/outputs`
- `POST /jobs/{job_id}/cancel`
- `GET /providers`

Run validation:

```powershell
python -m compileall -q web_core_reference app tests scripts\smoke_api.py
python -m pytest -q
python scripts\smoke_api.py
```

Provider secrets must come from environment variables or local ignored config, never from tracked files.