from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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

class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class JobParams(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = None
    source_language: str | None = None
    source_language_code: str | None = None
    target_language: str | None = None
    target_language_code: str | None = None
    detect_language: str | None = None
    subtitle_language: str | None = None
    recogn_type: int | None = None
    model_name: str | None = None
    translate_type: int | None = None
    tts_type: int | None = None
    voice_role: str | None = None
    app_mode: str | None = None
    subtitle_type: int | None = None
    output_srt: int | None = None
    recogn2pass: bool | None = None
    enable_diariz: bool | None = None
    nums_diariz: int | None = None
    speaker_clone_mode: str | None = None
    speaker_ref_min_seconds: int | None = None
    speaker_ref_max_seconds: int | None = None
    uuid: str | None = None
    target_dir: str | None = None
    dirname: str | None = None
    basename: str | None = None
    noextname: str | None = None
    ext: str | None = None
    targetdir_mp4: str | None = None

class JobCreate(ApiModel):
    type: JobType
    params: JobParams = Field(default_factory=JobParams)

class JobRead(ApiModel):
    id: str
    type: JobType
    status: JobStatus
    params: JobParams
    error: str | None = None
    target_dir: str | None = None
    created_at: str
    updated_at: str

class JobEventRead(ApiModel):
    id: int
    job_id: str
    type: str
    text: str
    created_at: str

class JobDetail(JobRead):
    events: list[JobEventRead] = Field(default_factory=list)

class OutputFile(ApiModel):
    path: str
    filename: str
    extension: str
    kind: Literal["subtitle", "audio", "video", "other"]
    size_bytes: int

class OutputList(ApiModel):
    job_id: str
    outputs: list[OutputFile]



class CloneVoiceRef(ApiModel):
    name: str
    path: str
    ref_text: str


class VoiceInfo(ApiModel):
    name: str
    value: str
    language: str | None = None
    gender: Literal["female", "male"] | None = None

class VoiceList(ApiModel):
    tts_type: int
    language: str | None = None
    voices: list[VoiceInfo]

class ProviderInfo(ApiModel):
    id: int
    name: str
    kind: Literal["stt", "tts", "translator"]
    runtime: Literal["local", "api"]
    key_name: str | None = None
    env_var: str | None = None
    configured: bool = False
    config_mode: Literal["env", "local", "provider"] = "provider"

class ProviderList(ApiModel):
    stt: list[ProviderInfo]
    tts: list[ProviderInfo]
    translators: list[ProviderInfo]
class RuntimeCheckRead(ApiModel):
    provider_kind: Literal["stt", "tts", "translator", "system"]
    provider_id: int | None = None
    provider_name: str
    status: Literal["ready", "missing"]
    missing: list[str] = Field(default_factory=list)
