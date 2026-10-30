"""
tests/test_assess.py
====================
Pytest test-suite for the three-question multimodal assessment endpoint
(POST /api/assess/multimodal) and the model metrics endpoint
(GET /api/model/metrics).

Run from the backend/ directory:
    pip install pytest httpx
    pytest tests/ -v

The tests use FastAPI's TestClient — no running server is needed.
The ML model is NOT loaded (no checkpoint files present in CI), so all
tests exercise the heuristic / demo fallback path, which is the correct
behaviour for a clean checkout.
"""

import io
import json
import struct
import wave
import sys
from pathlib import Path

import pytest

# Ensure backend/ is on sys.path so that main.py can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    """Create a TestClient once for the whole module."""
    from main import app
    return TestClient(app)


def _make_wav_bytes(duration_s: float = 0.5, sample_rate: int = 16000) -> bytes:
    """Generate a minimal valid WAV file in memory (sine-wave silent audio)."""
    n_samples = int(sample_rate * duration_s)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)      # 16-bit
        wf.setframerate(sample_rate)
        # Write silence (all zeros)
        wf.writeframes(b"\x00\x00" * n_samples)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# POST /api/assess/multimodal  — EATD three-question endpoint
# ---------------------------------------------------------------------------

class TestAssessEndpoint:

    def test_text_only_positive_returns_200(self, client):
        """Text-only submission for the positive question should succeed."""
        response = client.post(
            "/api/assess/multimodal",
            data={
                "positive_text": "I feel happy and energetic today.",
                "neutral_text":  "I woke up, had breakfast, and went to work.",
                "negative_text": "I am a bit tired sometimes.",
            },
        )
        assert response.status_code == 200, response.text

    def test_response_has_required_fields(self, client):
        """Response must include all required schema keys."""
        response = client.post(
            "/api/assess/multimodal",
            data={
                "positive_text": "I feel happy.",
                "neutral_text":  "Normal day.",
                "negative_text": "A little sad sometimes.",
            },
        )
        assert response.status_code == 200
        body = response.json()
        required = {
            "risk_level", "score", "confidence",
            "modality_contributions", "per_question_scores",
            "key_findings", "timestamp",
        }
        missing = required - body.keys()
        assert not missing, f"Missing fields in response: {missing}"

    def test_risk_level_is_valid(self, client):
        """risk_level must be one of the defined categories."""
        response = client.post(
            "/api/assess/multimodal",
            data={
                "positive_text": "I feel happy.",
                "neutral_text":  "Normal day.",
                "negative_text": "A little sad sometimes.",
            },
        )
        body = response.json()
        assert body["risk_level"] in {"low", "moderate", "elevated", "high", "critical"}

    def test_modality_contributions_keys(self, client):
        """modality_contributions must have 'text' and 'audio' keys."""
        response = client.post(
            "/api/assess/multimodal",
            data={
                "positive_text": "Feeling great.",
                "neutral_text":  "Just an ordinary day.",
                "negative_text": "A bit stressed.",
            },
        )
        body = response.json()
        mc = body["modality_contributions"]
        assert "text"  in mc, "missing 'text' in modality_contributions"
        assert "audio" in mc, "missing 'audio' in modality_contributions"

    def test_per_question_scores_length(self, client):
        """per_question_scores must contain exactly 3 items."""
        response = client.post(
            "/api/assess/multimodal",
            data={
                "positive_text": "Feeling great.",
                "neutral_text":  "Just a normal day.",
                "negative_text": "Some stress.",
            },
        )
        body = response.json()
        assert len(body["per_question_scores"]) == 3

    def test_high_risk_text_returns_high_or_critical(self, client):
        """Crisis keywords should push risk to high or critical."""
        response = client.post(
            "/api/assess/multimodal",
            data={
                "positive_text": "I see no reason to live.",
                "neutral_text":  "I want to end my life.",
                "negative_text": "Everything is hopeless and I want to die.",
            },
        )
        body = response.json()
        assert body["risk_level"] in {"high", "critical"}, \
            f"Expected high/critical for crisis text but got: {body['risk_level']}"

    def test_missing_all_text_returns_422(self, client):
        """Submitting with no text fields must return 422 Unprocessable Entity."""
        response = client.post("/api/assess/multimodal", data={})
        assert response.status_code == 422

    def test_with_valid_audio_file(self, client):
        """A valid WAV file should be accepted and increase audio confidence."""
        wav_bytes = _make_wav_bytes()
        response = client.post(
            "/api/assess/multimodal",
            data={
                "positive_text": "Feeling happy.",
                "neutral_text":  "Normal day.",
                "negative_text": "A bit tired.",
            },
            files={"positive_audio": ("test.wav", io.BytesIO(wav_bytes), "audio/wav")},
        )
        assert response.status_code == 200
        body = response.json()
        # With audio provided, audio contribution should be > 0
        assert body["modality_contributions"]["audio"] > 0

    def test_invalid_audio_content_type_returns_415(self, client):
        """Uploading a non-audio file (e.g. a PDF) should return 415."""
        fake_pdf = b"%PDF-1.4 fake content"
        response = client.post(
            "/api/assess/multimodal",
            data={
                "positive_text": "Feeling happy.",
                "neutral_text":  "Normal day.",
                "negative_text": "A bit tired.",
            },
            files={"positive_audio": ("report.pdf", io.BytesIO(fake_pdf), "application/pdf")},
        )
        assert response.status_code == 415, \
            f"Expected 415 for non-audio file but got {response.status_code}"

    def test_oversized_audio_returns_413(self, client):
        """An audio file exceeding MAX_AUDIO_SIZE_MB should return 413."""
        # 51 MB of zeros — well over the 50 MB limit
        big_audio = b"\x00" * (51 * 1024 * 1024)
        response = client.post(
            "/api/assess/multimodal",
            data={
                "positive_text": "Feeling okay.",
                "neutral_text":  "Normal day.",
                "negative_text": "Tired.",
            },
            files={"positive_audio": ("big.wav", io.BytesIO(big_audio), "audio/wav")},
        )
        assert response.status_code == 413, \
            f"Expected 413 for oversized file but got {response.status_code}"


# ---------------------------------------------------------------------------
# GET /api/model/metrics
# ---------------------------------------------------------------------------

class TestModelMetricsEndpoint:

    def test_returns_200(self, client):
        response = client.get("/api/model/metrics")
        # Either 200 (file found) or 404 (file absent — also acceptable)
        assert response.status_code in {200, 404}

    def test_response_has_models_key_when_200(self, client):
        response = client.get("/api/model/metrics")
        if response.status_code == 200:
            body = response.json()
            assert "models" in body, "Response must contain a 'models' list"

    def test_models_have_required_fields(self, client):
        response = client.get("/api/model/metrics")
        if response.status_code != 200:
            pytest.skip("metrics.json not present — skipping structure test")
        body = response.json()
        required = {"name", "description", "accuracy", "f1"}
        for model in body.get("models", []):
            missing = required - model.keys()
            assert not missing, f"Model entry missing fields: {missing}"
