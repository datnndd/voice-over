# 0018 Google Drive Output Sink

Date: 2026-06-09

## Status

Accepted

## Context

Job outputs can consume local disk. The user wants generated outputs uploaded to Google Drive and temporary local files removed after upload.

## Decision

Use a backend Google Drive service account configuration for the first implementation. Upload generated outputs after job success. Delete local upload/output directories only after all Drive uploads complete successfully. Store Drive file metadata in SQLite so `/jobs/{job_id}/outputs` can still report outputs after local cleanup.

## Alternatives Considered

1. Browser OAuth per user. More appropriate for multi-user hosted apps, but adds refresh-token storage and consent UI not needed for this local single-user tool.
2. Delete local files immediately after job success. Rejected because Drive upload failure would lose outputs.

## Consequences

Positive:

- Local storage is reclaimed after successful upload.
- Existing job API can keep reporting outputs through stored Drive metadata.

Tradeoffs:

- Requires Google service account setup and folder access.
- Automated tests use a fake uploader instead of real Drive credentials.

## Follow-Up

- Add OAuth user flow if this becomes a hosted multi-user app.
