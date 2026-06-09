# US-016 Downloads Processing Output

## Status

implemented

## Lane

normal

## Product Contract

Processing output directories are created under `C:\Users\ddat2\Downloads` by default. Operators can still override this with `VOICE_OVER_OUTPUTS`.

## Relevant Product Docs

- `docs/API_CONTRACT.md`
- `.env.example`

## Acceptance Criteria

- Default backend `outputs_dir` is `C:\Users\ddat2\Downloads`.
- Each job still creates its own UUID-named target directory under that folder.
- `VOICE_OVER_OUTPUTS` remains an override for other environments.
- API docs and env example describe the default.

## Design Notes

- Commands: no endpoint changes.
- Queries: `GET /jobs/{job_id}/outputs` continues to list files under job `target_dir`.
- API: response paths now default to `C:/Users/ddat2/Downloads/<job_id>/...`.
- Tables: no schema change.
- Domain rules: processing artifacts are filesystem outputs, not durable database records.
- UI surfaces: unchanged.

## Validation

When updating durable proof status, use numeric booleans:
`scripts/bin/harness-cli story update --id <id> --unit 1 --integration 1 --e2e 0 --platform 0`.

| Layer | Expected proof |
| --- | --- |
| Unit | `python -m compileall -q app_core app tests scripts\smoke_api.py`; `python -m pytest -q` |
| Integration | `python scripts\validate_phase1.py` |
| E2E | Not required for output path default. |
| Platform | Not required. |
| Release | Not required. |

## Harness Delta

No harness policy change.

## Evidence

- `python -m compileall -q app_core app tests scripts\smoke_api.py`
- `python -m pytest -q` -> 38 passed
- `python scripts\validate_phase1.py` -> 38 passed and smoke job succeeded
