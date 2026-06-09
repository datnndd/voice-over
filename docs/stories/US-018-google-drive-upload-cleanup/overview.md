# Overview

## Current Behavior

Users provide a local media path. Job outputs remain on local disk under the configured output directory after processing.

## Target Behavior

Users can upload source media through the API. After a job succeeds, generated output files are uploaded to Google Drive. Local job files are deleted only after the Drive upload succeeds.

## Affected Users

- Single backend/frontend user running voice-over jobs.

## Affected Product Docs

- `docs/API_CONTRACT.md`
- `.env.example`
- `README.md`

## Non-Goals

- OAuth browser consent flow.
- Sharing Drive files publicly.
- Deleting failed job outputs before operator inspection.
