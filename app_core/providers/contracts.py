from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal


class ProviderKind(StrEnum):
    stt = "stt"
    tts = "tts"
    translator = "translator"


class ProviderRuntime(StrEnum):
    local = "local"
    api = "api"


@dataclass(frozen=True)
class ProviderDescriptor:
    id: int
    name: str
    kind: ProviderKind
    runtime: ProviderRuntime
    key_name: str | None = None
    env_var: str | None = None
    legacy: Any | None = None

    @property
    def config_mode(self) -> Literal["env", "local", "provider"]:
        if self.env_var:
            return "env"
        if self.runtime == ProviderRuntime.local:
            return "local"
        return "provider"