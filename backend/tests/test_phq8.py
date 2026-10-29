"""
tests/test_phq8.py — Unit tests for PHQ-8 scoring logic.
Run: cd backend && python -m pytest tests/test_phq8.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from main import _phq8_severity, PHQ8_SEVERITY


# ── Severity band tests ───────────────────────────────────────────────────────

@pytest.mark.parametrize("score,expected_severity", [
    (0,  "Minimal"),
    (4,  "Minimal"),
    (5,  "Mild"),
    (9,  "Mild"),
    (10, "Moderate"),
    (14, "Moderate"),
    (15, "Moderately Severe"),
    (19, "Moderately Severe"),
    (20, "Severe"),
    (24, "Severe"),
])
def test_phq8_severity_bands(score, expected_severity):
    severity, _ = _phq8_severity(score)
    assert severity == expected_severity, f"score={score} expected {expected_severity}, got {severity}"


def test_phq8_all_zero():
    severity, desc = _phq8_severity(0)
    assert severity == "Minimal"
    assert "no depression" in desc.lower() or "little" in desc.lower()


def test_phq8_max_score():
    severity, desc = _phq8_severity(24)
    assert severity == "Severe"


def test_phq8_severity_has_description():
    for score in range(0, 25):
        severity, desc = _phq8_severity(score)
        assert severity, f"Empty severity for score {score}"
        assert desc,     f"Empty description for score {score}"


# ── Score calculation via HTTP (integration) ──────────────────────────────────

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_phq8_endpoint_valid():
    payload = {"answers": [1, 2, 0, 1, 0, 2, 1, 0], "user_id": "test"}
    resp = client.post("/api/phq8/score", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 7
    assert data["severity"] == "Mild"
    assert "answers" in data
    assert len(data["answers"]) == 8


def test_phq8_endpoint_rejects_invalid_answer():
    payload = {"answers": [0, 0, 0, 4, 0, 0, 0, 0]}  # 4 is out of range
    resp = client.post("/api/phq8/score", json=payload)
    assert resp.status_code == 422


def test_phq8_endpoint_rejects_too_few_answers():
    payload = {"answers": [1, 2, 3]}
    resp = client.post("/api/phq8/score", json=payload)
    assert resp.status_code == 422


def test_phq8_endpoint_max_score():
    payload = {"answers": [3, 3, 3, 3, 3, 3, 3, 3]}
    resp = client.post("/api/phq8/score", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 24
    assert data["severity"] == "Severe"
