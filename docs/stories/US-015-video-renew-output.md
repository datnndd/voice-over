# US-015 Video Renew Output

## Status

implemented

## Lane

normal

## Product Contract

`video_translate` returns separate output assets instead of muxing translated voice into the source video. The video output is a copy of the original source video named `video_renew.<ext>`.

## Relevant Product Docs

- `docs/API_CONTRACT.md`

## Acceptance Criteria

- A video translation job does not split the source video into a no-audio `novoice` intermediate.
- A video translation job does not run final video/audio/subtitle muxing.
- Output files include `source.srt`, `target.srt`, `voice_target.m4a`, and `video_renew.<ext>` when the selected providers complete successfully.
- `video_renew.<ext>` is a direct copy of the input video.

## Design Notes

- Commands: `POST /jobs` keeps the same job type.
- Queries: `GET /jobs/{job_id}/outputs` lists the four independent assets.
- API: `targetdir_mp4` now points to `video_renew.<ext>`.
- Tables: no database schema change.
- Domain rules: translated voice is an independent output asset, not embedded in the returned video.
- UI surfaces: frontend can choose the video copy and audio output independently.

## Validation

When updating durable proof status, use numeric booleans:
`scripts/bin/harness-cli story update --id <id> --unit 1 --integration 1 --e2e 0 --platform 0`.

| Layer | Expected proof |
| --- | --- |
| Unit | `python -m compileall -q app_core app tests scripts\smoke_api.py` |
| Integration | `python -m pytest -q` |
| E2E | Not required for this backend-only behavior change. |
| Platform | Real provider smoke optional because it requires configured providers. |
| Release | Not required. |

## Harness Delta

No harness policy change.

## Evidence

- `python -m compileall -q app_core app tests scripts\smoke_api.py`
- `python -m pytest -q` -> 36 passed
- `python scripts\validate_phase1.py` -> 36 passed and smoke job succeeded
