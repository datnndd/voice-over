from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUTS_DIR = Path(r"C:\Users\ddat2\Downloads")
DEFAULT_UPLOADS_DIR = ROOT_DIR / "data" / "uploads"


def parse_csv_env(name: str) -> frozenset[str]:
    raw = os.getenv(name, "")
    return frozenset(item.strip().lower() for item in raw.split(",") if item.strip())

def parse_list_env(name: str, default: str = "") -> tuple[str, ...]:
    raw = os.getenv(name, default)
    return tuple(item.strip() for item in raw.split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    database_path: Path = field(default_factory=lambda: Path(os.getenv("VOICE_OVER_DB", ROOT_DIR / "data" / "voice_over.db")))
    outputs_dir: Path = field(default_factory=lambda: Path(os.getenv("VOICE_OVER_OUTPUTS", DEFAULT_OUTPUTS_DIR)))
    uploads_dir: Path = field(default_factory=lambda: Path(os.getenv("VOICE_OVER_UPLOADS", DEFAULT_UPLOADS_DIR)))
    google_drive_enabled: bool = field(default_factory=lambda: os.getenv("VOICE_OVER_GOOGLE_DRIVE_ENABLED", "0") == "1")
    google_drive_folder_id: str = field(default_factory=lambda: os.getenv("VOICE_OVER_GOOGLE_DRIVE_FOLDER_ID", ""))
    google_drive_credentials_file: Path | None = field(default_factory=lambda: Path(value) if (value := os.getenv("VOICE_OVER_GOOGLE_DRIVE_CREDENTIALS_FILE", "")) else None)
    google_drive_credentials_json: str = field(default_factory=lambda: os.getenv("VOICE_OVER_GOOGLE_DRIVE_CREDENTIALS_JSON", ""))
    worker_enabled: bool = field(default_factory=lambda: os.getenv("VOICE_OVER_WORKER", "1") != "0")
    provider_allow: frozenset[str] = field(default_factory=lambda: parse_csv_env("VOICE_OVER_PROVIDER_ALLOW"))
    provider_deny: frozenset[str] = field(default_factory=lambda: parse_csv_env("VOICE_OVER_PROVIDER_DENY"))
    frontend_origins: tuple[str, ...] = field(
        default_factory=lambda: parse_list_env(
            "VOICE_OVER_FRONTEND_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
    )


settings = Settings()
