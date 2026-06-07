from __future__ import annotations

from pathlib import Path

from app.db import JobRepository
from app.models import JobCreate, JobType
from app.service import JobService
from app.worker import JobWorker


class FakeFacade:
    def run_stt(self, params):
        output = Path(params["target_dir"]) / "result.srt"
        output.write_text("1\n00:00:00,000 --> 00:00:01,000\nhello\n", encoding="utf-8")
        return {"status": "success", "target_dir": params["target_dir"], "outputs": [output.as_posix()], "error": None}

    def run_tts(self, params):
        return self.run_stt(params)

    def run_subtitle_translate(self, params):
        return self.run_stt(params)

    def run_video_translate(self, params):
        return self.run_stt(params)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    input_video = root / "test.mp4"
    if not input_video.exists():
        raise SystemExit("test.mp4 not found")

    smoke_dir = root / "data" / "smoke"
    repo = JobRepository(smoke_dir / "smoke.db")
    worker = JobWorker(repo, FakeFacade())
    service = JobService(repo, worker, smoke_dir / "outputs")
    job = service.create_job(JobCreate(type=JobType.stt, params={"name": input_video.as_posix()}))
    result = worker.run_once(job.id)
    print({"job_id": job.id, "status": result["status"], "target_dir": result["target_dir"]})


if __name__ == "__main__":
    main()