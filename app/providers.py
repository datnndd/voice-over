from __future__ import annotations

from typing import Any

from app.config import settings
from app.models import ProviderInfo, ProviderList
from app_core.providers import ProviderDescriptor, ProviderKind, descriptor_from_legacy, is_configured


def _provider_tokens(descriptor: ProviderDescriptor) -> set[str]:
    return {
        f"{descriptor.kind.value}:{descriptor.id}",
        f"{descriptor.kind.value}:*",
        descriptor.runtime.value,
        "*",
    }


def _provider_enabled(descriptor: ProviderDescriptor) -> bool:
    tokens = _provider_tokens(descriptor)
    if settings.provider_allow and not tokens.intersection(settings.provider_allow):
        return False
    if settings.provider_deny and tokens.intersection(settings.provider_deny):
        return False
    return True


def _provider_items(kind: ProviderKind, registry: dict[int, Any]) -> list[ProviderInfo]:
    items: list[ProviderInfo] = []
    for provider_id, provider in registry.items():
        descriptor = descriptor_from_legacy(kind, provider_id, provider)
        if not _provider_enabled(descriptor):
            continue
        items.append(
            ProviderInfo(
                id=descriptor.id,
                name=descriptor.name,
                kind=descriptor.kind.value,  # type: ignore[arg-type]
                runtime=descriptor.runtime.value,  # type: ignore[arg-type]
                key_name=descriptor.key_name,
                env_var=descriptor.env_var,
                configured=is_configured(descriptor),
                config_mode=descriptor.config_mode,
            )
        )
    return items


def list_providers() -> ProviderList:
    from app_core import recognition, translator, tts

    return ProviderList(
        stt=_provider_items(ProviderKind.stt, recognition._ID_NAME_DICT),
        tts=_provider_items(ProviderKind.tts, tts._ID_NAME_DICT),
        translators=_provider_items(ProviderKind.translator, translator._ID_NAME_DICT),
    )