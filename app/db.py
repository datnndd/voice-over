from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from app.models import JobStatus, JobType


SCHEMA = """
create table if not exists jobs (
    id text primary key,
    type text not null,
    status text not null,
    params_json text not null,
    error text,
    target_dir text,
    progress_percent integer not null default 0,
    created_at text not null default (datetime('now')),
    updated_at text not null default (datetime('now'))
);

create table if not exists job_events (
    id integer primary key autoincrement,
    job_id text not null,
    type text not null,
    text text not null,
    created_at text not null default (datetime('now')),
    foreign key(job_id) references jobs(id)
);

create table if not exists job_drive_outputs (
    id integer primary key autoincrement,
    job_id text not null,
    local_path text not null,
    filename text not null,
    extension text not null,
    kind text not null,
    size_bytes integer not null,
    drive_file_id text not null,
    drive_web_view_link text,
    created_at text not null default (datetime('now')),
    foreign key(job_id) references jobs(id)
);
"""


class JobRepository:
    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            columns = {row[1] for row in conn.execute("pragma table_info(jobs)").fetchall()}
            if "progress_percent" not in columns:
                conn.execute("alter table jobs add column progress_percent integer not null default 0")

    def create_job(self, job_id: str, job_type: JobType, params: dict[str, Any], target_dir: str) -> dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                """
                insert into jobs (id, type, status, params_json, target_dir)
                values (?, ?, ?, ?, ?)
                """,
                (job_id, job_type.value, JobStatus.queued.value, json.dumps(params), target_dir),
            )
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("select * from jobs where id = ?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(job_id)
        return self._job_from_row(row)

    def update_status(
        self,
        job_id: str,
        status: JobStatus,
        *,
        error: str | None = None,
        target_dir: str | None = None,
        progress_percent: int | None = None,
    ) -> dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                """
                update jobs
                set status = ?,
                    error = coalesce(?, error),
                    target_dir = coalesce(?, target_dir),
                    progress_percent = coalesce(?, progress_percent),
                    updated_at = datetime('now')
                where id = ?
                """,
                (status.value, error, target_dir, progress_percent, job_id),
            )
        return self.get_job(job_id)

    def update_progress(self, job_id: str, progress_percent: int) -> dict[str, Any]:
        progress = max(0, min(100, int(progress_percent)))
        with self._connect() as conn:
            conn.execute(
                """
                update jobs
                set progress_percent = max(progress_percent, ?), updated_at = datetime('now')
                where id = ?
                """,
                (progress, job_id),
            )
        return self.get_job(job_id)

    def add_event(self, job_id: str, event_type: str, text: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "insert into job_events (job_id, type, text) values (?, ?, ?)",
                (job_id, event_type, text),
            )

    def add_drive_output(self, job_id: str, output: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                insert into job_drive_outputs (
                    job_id, local_path, filename, extension, kind, size_bytes,
                    drive_file_id, drive_web_view_link
                ) values (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    output["local_path"],
                    output["filename"],
                    output["extension"],
                    output["kind"],
                    output["size_bytes"],
                    output["drive_file_id"],
                    output.get("drive_web_view_link"),
                ),
            )

    def list_drive_outputs(self, job_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "select * from job_drive_outputs where job_id = ? order by id asc",
                (job_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_events(self, job_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "select * from job_events where job_id = ? order by id asc",
                (job_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def _job_from_row(self, row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["params"] = json.loads(data.pop("params_json"))
        return data

