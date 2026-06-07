from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    database_path: Path = Path(os.getenv("VOICE_OVER_DB", ROOT_DIR / "data" / "voice_over.db"))
    outputs_dir: Path = Path(os.getenv("VOICE_OVER_OUTPUTS", ROOT_DIR / "outputs"))
    worker_enabled: bool = os.getenv("VOICE_OVER_WORKER", "1") != "0"


settings = Settings()

