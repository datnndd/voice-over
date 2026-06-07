from __future__ import annotations

from typing import Any

from app.models import ProviderInfo, ProviderList


def _provider_items(kind: str, registry: dict[int, Any]) -> list[ProviderInfo]:
    items: list[ProviderInfo] = []
    for provider_id, provider in registry.items():
        key_name = getattr(provider, "key_name", None)
        items.append(
            ProviderInfo(
                id=provider_id,
                name=getattr(provider, "name", str(provider_id)),
                kind=kind,  # type: ignore[arg-type]
                key_name=key_name,
                config_mode="env" if key_name else "provider",
            )
        )
    return items


def list_providers() -> ProviderList:
    from web_core_reference import recognition, translator, tts

    return ProviderList(
        stt=_provider_items("stt", recognition._ID_NAME_DICT),
        tts=_provider_items("tts", tts._ID_NAME_DICT),
        translators=_provider_items("translator", translator._ID_NAME_DICT),
    )

