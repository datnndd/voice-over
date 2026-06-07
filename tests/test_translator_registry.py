from __future__ import annotations

from pathlib import Path

from app_core import translator


def test_translator_registry_only_keeps_openai_and_deepseek():
    assert set(translator._ID_NAME_DICT) == {translator.CHATGPT_INDEX, translator.DEEPSEEK_INDEX}
    assert set(translator.AI_TRANS_CHANNELS) == {translator.CHATGPT_INDEX, translator.DEEPSEEK_INDEX}
    names = " ".join(provider.name for provider in translator._ID_NAME_DICT.values()).lower()
    assert "openai" in names
    assert "deepseek" in names
    forbidden = ["gemini", "azure", "local llm", "openrouter", "google", "deepl", "baidu", "qwen"]
    assert all(item not in names for item in forbidden)


def test_removed_translator_modules_are_not_present():
    remaining = {path.name for path in Path("app_core/translator").glob("*.py")}
    assert remaining == {
        "__init__.py",
        "_base.py",
        "_chatgpt.py",
        "_deepseek.py",
        "_openaicompat.py",
    }


def test_removed_llm_prompts_are_not_present():
    expected = {"chatgpt.txt", "deepseek.txt"}
    assert {path.name for path in Path("app_core/prompts/srt").glob("*.txt")} == expected
    assert {path.name for path in Path("app_core/prompts/text").glob("*.txt")} == expected