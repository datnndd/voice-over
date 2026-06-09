# US-021 SRT To Audio Workflow

## Status

implemented

## Lane

normal

## Product Contract

Users can create an audio file directly from a local SRT file by selecting an audio language, TTS provider, and voice role. The frontend submits a `tts` job and the backend writes the synthesized audio under the local Downloads output folder for that job.

## Relevant Product Docs

- `docs/API_CONTRACT.md`

## Acceptance Criteria

- User can choose `SRT -> audio` from the create-job UI.
- SRT-to-audio mode only requires SRT path, audio language, TTS provider, and voice role.
- Frontend submits `POST /jobs` with `type: "tts"` for this mode.
- Backend normalizes SRT input paths and creates a job cache folder for `DubbingSrt`.
- Successful output is listed as an audio file by `GET /jobs/{job_id}/outputs`.

## Design Notes

- Commands: `POST /jobs` with `type: "tts"`.
- Queries: existing job detail and output list endpoints.
- API: no new endpoint; reuses stable job contract.
- Tables: none.
- Domain rules: SRT-to-audio does not require STT or translator readiness.
- UI surfaces: create-job panel adds `SRT -> audio` mode.

## Validation

When updating durable proof status, use numeric booleans:
`scripts/bin/harness-cli story update --id <id> --unit 1 --integration 1 --e2e 0 --platform 0`.

| Layer | Expected proof |
| --- | --- |
| Unit | `python -m pytest -q` |
| Integration | `python scripts\\validate_phase1.py` |
| E2E | Not required for this slice. |
| Platform | `cd frontend && npm run lint && npm run build` |
| Release | Not required. |

## Harness Delta

No harness policy changes.

## Evidence

Pending validation in this run.
