# US-019 Local Downloads Only

## Status

implemented

## Lane

normal

## Product Contract

The app processes media from a local filesystem path and writes outputs under `C:\Users\ddat2\Downloads` by default. It does not upload videos through the API and does not upload outputs to Google Drive.

## Relevant Product Docs

- `README.md`
- `.env.example`
- `docs/API_CONTRACT.md`

## Acceptance Criteria

- No `/uploads/media` endpoint exists.
- No Google Drive uploader/config/runtime check remains in app code.
- Frontend requires a local video path instead of file upload.
- Outputs remain local and are returned by `/jobs/{job_id}/outputs`.

## Design Notes

- Commands: `POST /jobs` remains the only job input path.
- Queries: `GET /jobs/{job_id}/outputs` returns local files only.
- API: `OutputFile` has local path fields only.
- Tables: no Drive metadata table.
- Domain rules: local output retention is user-managed in Downloads.
- UI surfaces: upload input removed.

## Validation

| Layer | Expected proof |
| --- | --- |
| Unit | `python -m compileall -q app_core app tests scripts\smoke_api.py`; `python -m pytest -q` |
| Integration | `python scripts\validate_phase1.py` |
| E2E | Not required. |
| Platform | `cd frontend && npm run lint`; `cd frontend && npm run build` |
| Release | Not required. |

## Harness Delta

No harness policy change.

## Evidence

- `python -m compileall -q app_core app tests scripts\smoke_api.py`
- `python -m pytest -q` -> 40 passed
- `python scripts\validate_phase1.py` -> 40 passed and smoke job succeeded
- `cd frontend && npm run lint`
- `cd frontend && npm run build`
