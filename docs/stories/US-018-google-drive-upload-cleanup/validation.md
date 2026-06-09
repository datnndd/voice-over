# Validation

## Proof Strategy

Use unit tests with fake Drive uploader to prove upload-before-delete behavior and no cleanup on upload failure. Avoid real Google calls in automated tests.

## Test Plan

| Layer | Cases |
| --- | --- |
| Unit | Media upload saves files safely; worker uploads outputs and deletes local files after success; worker preserves files on upload failure. |
| Integration | API outputs include Drive metadata after fake upload. |
| E2E | Not required for first backend slice. |
| Platform | Real Drive smoke optional with configured credentials. |
| Performance | Not required. |
| Logs/Audit | Job events include Drive upload and cleanup messages. |

## Fixtures

- Temporary SQLite database.
- Temporary upload/output roots.
- Fake Drive uploader returning deterministic file ids and links.

## Commands

```text
python -m compileall -q app_core app tests scripts\smoke_api.py
python -m pytest -q
python scripts\validate_phase1.py
```

## Acceptance Evidence

- `python -m compileall -q app_core app tests scripts\smoke_api.py`
- `python -m pytest -q` -> 44 passed
- `python scripts\validate_phase1.py` -> 44 passed and smoke job succeeded
- `cd frontend && npm run lint`
- `cd frontend && npm run build`
