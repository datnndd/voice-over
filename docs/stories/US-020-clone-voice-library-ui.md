# US-020 Clone Voice Library UI

## Status

implemented

## Lane

normal

## Product Contract

The frontend provides a separate voice library panel for clone-capable TTS providers. Users upload a reference audio and transcript once, then the saved voice is selected automatically for single voice jobs.

## Relevant Product Docs

- `docs/API_CONTRACT.md`

## Acceptance Criteria

- Clone voice creation is not embedded inside the single voice provider form.
- The voice library lets users choose a clone-capable TTS model before upload.
- Saved clone voices refresh the target provider voice list.
- After upload, the app switches to single voice with the selected clone provider and saved voice role.

## Design Notes

- Commands: `POST /voices/clone-refs` remains the backend creation endpoint.
- Queries: `/voices?tts_type=...` refreshes the selected provider voice list.
- API: no response schema change.
- Tables: no schema change.
- Domain rules: uploaded clone roles are reusable single voice choices.
- UI surfaces: dashboard side panel `Voice library`.

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
