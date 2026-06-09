# Exec Plan

## Goal

Upload successful job outputs to Google Drive and clean up local processing files after upload.

## Scope

In scope:

- Backend media upload endpoint.
- Google Drive service-account uploader.
- Drive output metadata in SQLite.
- Local cleanup after successful Drive upload.
- API docs and tests.

Out of scope:

- Google OAuth UI.
- Public sharing permissions.
- Retry queue for Drive outages.

## Risk Classification

Risk flags:

- External systems.
- Data model.
- Public contracts.
- Existing behavior.
- Data deletion/retention.

Hard gates:

- External provider behavior.
- Data deletion.

## Work Phases

1. Discovery.
2. Design.
3. Validation planning.
4. Implementation.
5. Verification.
6. Harness update.

## Stop Conditions

Pause for human confirmation if:

- Cleanup would delete files outside configured upload/output roots.
- Drive upload cannot be made conditional on success.
- Validation requires real Google credentials.
