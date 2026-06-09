from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_voices_endpoint_returns_azure_voices_by_language():
    with TestClient(app) as client:
        response = client.get("/voices", params={"tts_type": 28, "language": "vi"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["tts_type"] == 28
    assert payload["language"] == "vi"
    names = [voice["name"] for voice in payload["voices"]]
    assert "No" in names
    assert "HoaiMy(Female)" in names


def test_voices_endpoint_returns_omnivoice_clone_roles():
    with TestClient(app) as client:
        response = client.get("/voices", params={"tts_type": 2, "language": "vi"})

    assert response.status_code == 200
    names = [voice["name"] for voice in response.json()["voices"]]
    assert "No" in names
    assert "clone" in names

def test_voices_endpoint_returns_vieneu_roles():
    with TestClient(app) as client:
        response = client.get("/voices", params={"tts_type": 32, "language": "vi"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["tts_type"] == 32
    names = [voice["name"] for voice in payload["voices"]]
    assert "No" in names
    assert "clone" in names
    assert "Ngoc" in names


def test_upload_clone_reference_adds_omnivoice_role():
    audio = b"RIFF0000WAVEfmt "
    with TestClient(app) as client:
        response = client.post(
            "/voices/clone-refs",
            files={"file": ("sample.wav", audio, "audio/wav")},
            data={"ref_text": "hello sample"},
        )
        voices = client.get("/voices", params={"tts_type": 2, "language": "vi"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "sample.wav"
    names = [voice["name"] for voice in voices.json()["voices"]]
    assert "sample.wav" in names
    try:
        Path(payload["path"]).unlink(missing_ok=True)
    except PermissionError:
        pass
