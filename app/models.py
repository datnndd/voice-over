from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field

class JobType(StrEnum):
    stt = "stt"
    tts = "tts"
    subtitle_translate = "subtitle_translate"
    video_translate = "video_translate"

class JobStatus(StrEnum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
    canceled = "canceled"

class JobCreate(BaseModel):
    type: JobType
    params: dict[str, Any] = Field(default_factory=dict)

class JobRead(BaseModel):
    id: str
    type: JobType
    status: JobStatus
    params: dict[str, Any]
    error: str | None = None
    target_dir: str | None = None
    created_at: str
    updated_at: str

class JobEventRead(BaseModel):
    id: int
    job_id: str
    type: str
    text: str
    created_at: str

class JobDetail(JobRead):
    events: list[JobEventRead] = Field(default_factory=list)

class OutputList(BaseModel):
    job_id: str
    outputs: list[str]

class ProviderInfo(BaseModel):
    id: int
    name: str
    kind: Literal["stt", "tts", "translator"]
    runtime: Literal["local", "api"]
    key_name: str | None = None
    env_var: str | None = None
    configured: bool = False
    config_mode: Literal["env", "local", "provider"] = "provider"

class ProviderList(BaseModel):
    stt: list[ProviderInfo]
    tts: list[ProviderInfo]
    translators: list[ProviderInfo]
class RuntimeCheckRead(BaseModel):
    provider_kind: str
    provider_id: int | None = None
    provider_name: str
    status: Literal["ready", "missing"]
    missing: list[str] = Field(default_factory=list)
