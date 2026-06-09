from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from app.models import OutputFile

DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.file"


@dataclass(frozen=True)
class DriveUploadResult:
    local_path: str
    filename: str
    extension: str
    kind: str
    size_bytes: int
    drive_file_id: str
    drive_web_view_link: str | None = None

    def to_record(self) -> dict[str, object]:
        return {
            "local_path": self.local_path,
            "filename": self.filename,
            "extension": self.extension,
            "kind": self.kind,
            "size_bytes": self.size_bytes,
            "drive_file_id": self.drive_file_id,
            "drive_web_view_link": self.drive_web_view_link,
        }


class GoogleDriveUploader:
    def __init__(self, *, credentials_file: Path | None, credentials_json: str, folder_id: str) -> None:
        self.credentials_file = credentials_file
        self.credentials_json = credentials_json
        self.folder_id = folder_id

    def _credentials(self):
        try:
            from google.oauth2 import service_account
        except ImportError as exc:
            raise RuntimeError("Google Drive dependencies are missing. Install package extras: .[providers]") from exc

        if self.credentials_json:
            info = json.loads(self.credentials_json)
            return service_account.Credentials.from_service_account_info(info, scopes=[DRIVE_SCOPE])
        if self.credentials_file:
            return service_account.Credentials.from_service_account_file(self.credentials_file, scopes=[DRIVE_SCOPE])
        raise RuntimeError("Google Drive credentials are not configured")

    def _service(self):
        try:
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise RuntimeError("Google Drive dependencies are missing. Install package extras: .[providers]") from exc
        return build("drive", "v3", credentials=self._credentials(), cache_discovery=False)

    def upload_outputs(self, outputs: list[OutputFile]) -> list[DriveUploadResult]:
        if not self.folder_id:
            raise RuntimeError("Google Drive folder id is not configured")
        try:
            from googleapiclient.http import MediaFileUpload
        except ImportError as exc:
            raise RuntimeError("Google Drive dependencies are missing. Install package extras: .[providers]") from exc

        service = self._service()
        uploaded: list[DriveUploadResult] = []
        for output in outputs:
            metadata = {"name": output.filename, "parents": [self.folder_id]}
            media = MediaFileUpload(output.path, resumable=True)
            response = service.files().create(
                body=metadata,
                media_body=media,
                fields="id,webViewLink",
            ).execute()
            uploaded.append(
                DriveUploadResult(
                    local_path=output.path,
                    filename=output.filename,
                    extension=output.extension,
                    kind=output.kind,
                    size_bytes=output.size_bytes,
                    drive_file_id=str(response["id"]),
                    drive_web_view_link=response.get("webViewLink"),
                )
            )
        return uploaded
