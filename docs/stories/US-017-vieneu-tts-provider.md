# US-017 VieNeu TTS Provider

## Status

implemented

## Lane

normal

## Product Contract

VieNeu-TTS is available as a selectable TTS provider with `tts_type=32`. It uses the optional `vieneu` Python SDK and can synthesize with preset roles or clone references.

## Relevant Product Docs

- `docs/API_CONTRACT.md`
- `.env.example`

## Acceptance Criteria

- `/providers` includes VieNeu-TTS as a TTS option.
- `/voices?tts_type=32&language=vi` returns `No`, `clone`, and configured preset voices.
- Runtime checks report whether the `vieneu` Python module is installed.
- TTS dispatch can call VieNeu SDK `infer` and `save` without requiring real provider calls in unit tests.
- Clone reference uploads can be used as VieNeu roles.

## Design Notes

- Commands: no endpoint changes.
- Queries: `/providers`, `/voices`.
- API: `tts_type=32` selects VieNeu-TTS.
- Tables: no schema change.
- Domain rules: VieNeu is optional runtime provider; missing SDK reports readiness failure instead of hiding provider.
- UI surfaces: existing provider and voice selectors should show it automatically.

## Validation

When updating durable proof status, use numeric booleans:
`scripts/bin/harness-cli story update --id <id> --unit 1 --integration 1 --e2e 0 --platform 0`.

| Layer | Expected proof |
| --- | --- |
| Unit | `python -m compileall -q app_core app tests scripts\smoke_api.py`; `python -m pytest -q` |
| Integration | `python scripts\validate_phase1.py` |
| E2E | Not required for provider registry integration. |
| Platform | Real VieNeu synthesis optional because SDK/model runtime may not be installed locally. |
| Release | Not required. |

## Harness Delta

No harness policy change.

## Evidence

- `python -m compileall -q app_core app tests scripts\smoke_api.py`
- `python -m pytest -q` -> 40 passed
- `python scripts\validate_phase1.py` -> 40 passed and smoke job succeeded
- `python -c "from app.providers import list_providers; print([(p.id,p.name,p.runtime,p.configured) for p in list_providers().tts])"` -> includes `(32, 'VieNeu-TTS', 'local', True)`
