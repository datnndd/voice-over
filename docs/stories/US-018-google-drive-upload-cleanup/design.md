# Design

## Domain Model

Uploaded media is a local input asset. Job outputs are generated local assets. Drive uploads are remote output records containing filename, file id, web view link, and size.

## Application Flow

1. `POST /uploads/media` stores user media under an upload directory and returns a local path for job params.
2. `POST /jobs` continues to enqueue existing job types.
3. On job success, the worker lists local outputs and uploads them to Google Drive when Drive is configured.
4. Local job output directory and uploaded input file are deleted only after all selected Drive uploads succeed.

## Interface Contract

- `POST /uploads/media` accepts multipart file upload and returns `UploadedMedia`.
- `GET /jobs/{job_id}/outputs` returns local files while present and Drive file records after upload.
- Job events include `drive` messages for upload and cleanup.

## Data Model

SQLite adds a `job_drive_outputs` table with job id, local path, filename, Drive file id/link, size, and upload timestamp. Existing job rows remain unchanged.

## UI / Platform Impact

Frontend can upload a video file before creating a job and use returned path as `params.name`. Existing path entry remains usable for local runs.

## Observability

Drive upload start/success/cleanup/failure is recorded as job events. Secrets are not logged.

## Alternatives Considered

1. OAuth user consent per browser user. Rejected for first slice because this app is single-user/local and service account config is simpler to validate without storing refresh tokens.
