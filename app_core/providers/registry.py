from __future__ import annotations

import os
from typing import Any

from app_core.providers.contracts import ProviderDescriptor, ProviderKind, ProviderRuntime


def env_var_for_key(key_name: str | None) -> str | None:
    if not key_name:
        return None
    normalized = "".join(ch if ch.isalnum() else "_" for ch in key_name).upper()
    return f"VOICE_OVER_{normalized}"


def descriptor_from_legacy(kind: ProviderKind, provider_id: int, provider: Any) -> ProviderDescriptor:
    key_name = getattr(provider, "key_name", None)
    runtime = ProviderRuntime.api if key_name else ProviderRuntime.local
    return ProviderDescriptor(
        id=provider_id,
        name=getattr(provider, "name", str(provider_id)),
        kind=kind,
        runtime=runtime,
        key_name=key_name,
        env_var=env_var_for_key(key_name),
        legacy=provider,
    )


def is_configured(descriptor: ProviderDescriptor) -> bool:
    if descriptor.runtime == ProviderRuntime.local:
        return True
    if not descriptor.env_var:
        return False
    return bool(os.getenv(descriptor.env_var))