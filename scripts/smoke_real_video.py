from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from app.models import JobCreate, JobType
from app.runtime_checks import check_runtime
from app.service import JobService
from app.db import JobRepository
from app.worker import JobWorker
from app.config import ROOT_DIR


def default_payload(video_path: Path) -> dict:
    return {
        "name": video_path.as_posix(),
        "source_language": "en",
        "source_language_code": "en",
        "target_language": "vi",
        "target_language_code": "vi",
        "detect_language": "en",
        "subtitle_language": "vi",
        "recogn_type": 10,
        "model_name": "nova-3",
        "translate_type": 3,
        "tts_type": 28,
        "voice_role": os.getenv("VOICE_OVER_DEFAULT_VOICE_ROLE", "HoaiMy(Female)"),
        "app_mode": "biaozhun",
        "subtitle_type": 0,
        "output_srt": 0,
        "recogn2pass": False,
    }


def print_checks(required: set[tuple[str, int | None]] | None = None) -> bool:
    checks = check_runtime()
    ok = True
    for check in checks:
        print(json.dumps(check.__dict__, ensure_ascii=False))
        selected = required is None or (check.provider_kind, check.provider_id) in required
        if selected and check.status != "ready":
            ok = False
    return ok


def required_checks_for_payload(payload: dict) -> set[tuple[str, int | None]]:
    return {
        ("stt", int(payload["recogn_type"])),
        ("tts", int(payload["tts_type"])),
        ("translator", int(payload["translate_type"])),
        ("system", None),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check real video runtime readiness and optionally enqueue a real job.")
    parser.add_argument("--video", default=(ROOT_DIR / "test.mp4").as_posix())
    parser.add_argument("--run", action="store_true", help="enqueue a real video_translate job after checks pass")
    args = parser.parse_args()

    video_path = Path(args.video).resolve()
    if not video_path.exists():
        raise SystemExit(f"video not found: {video_path}")

    payload = default_payload(video_path)
    ready = print_checks(required_checks_for_payload(payload) if args.run else None)
    print(json.dumps({"job_type": "video_translate", "params": payload}, ensure_ascii=False, indent=2))
    if not args.run:
        return
    if not ready:
        raise SystemExit("selected runtime checks failed; fill .env/install dependencies before --run")

    smoke_dir = ROOT_DIR / "data" / "real_smoke"
    repo = JobRepository(smoke_dir / "real_smoke.db")
    worker = JobWorker(repo)
    service = JobService(repo, worker, smoke_dir / "outputs")
    job = service.create_job(JobCreate(type=JobType.video_translate, params=payload))
    result = worker.run_once(job.id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()