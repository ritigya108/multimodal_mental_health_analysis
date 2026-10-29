"""
tests/test_multimodal.py — Unit tests for the multimodal assessment endpoint.
Run: cd backend && python -m pytest tests/test_multimodal.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient
from main import app, _heuristic_analysis

client = TestClient(app)


# ── Heuristic logic ───────────────────────────────────────────────────────────

def test_heuristic_low_risk():
    result = _heuristic_analysis("I feel great today. Everything is going well.", False, False)
    assert result["risk_level"] == "low"
    assert result["score"] < 0.5
    assert "key_findings" in result
    assert len(result["key_findings"]) == 3


def test_heuristic_high_risk_crisis():
    result = _heuristic_analysis("I want to kill myself and end my life.", False, False)
    assert result["risk_level"] == "critical"
    assert result["crisis_flags"]["high_risk_detected"] is True
    assert result["score"] > 0.5


def test_heuristic_moderate_risk():
    result = _heuristic_analysis(
        "I feel sad and tired most days. Things are difficult.", False, False
    )
    assert result["risk_level"] in ("moderate", "high")
    assert 0.1 <= result["score"] <= 1.0


def test_heuristic_modality_contributions_sum():
    result = _heuristic_analysis("I feel fine.", True, True)
    contribs = result["modality_contributions"]
    total = contribs["text"] + contribs["audio"] + contribs["video"]
    assert abs(total - 100.0) < 0.5, f"Contributions should sum to ~100%, got {total}"


def test_heuristic_text_only_modality():
    result = _heuristic_analysis("Neutral text here.", False, False)
    assert result["modality_contributions"]["audio"] == 0.0
    assert result["modality_contributions"]["video"] == 0.0
    # text_conf (0.85) / max(0.85, 1) * 100 = 85.0 — audio/video are 0 so text dominates
    assert result["modality_contributions"]["text"] > 80.0


def test_heuristic_input_type_flag():
    r_text  = _heuristic_analysis("test", False, False)
    r_audio = _heuristic_analysis("test", True,  False)
    r_video = _heuristic_analysis("test", False, True)
    r_both  = _heuristic_analysis("test", True,  True)
    assert r_text["input_type"]  == "text"
    assert r_audio["input_type"] == "audio"
    assert r_video["input_type"] == "video"
    assert r_both["input_type"]  == "combined"


# ── Endpoint tests ────────────────────────────────────────────────────────────

def test_assess_endpoint_text_only():
    resp = client.post(
        "/api/assess/multimodal",
        data={"text": "I have been feeling hopeless and sad for weeks.", "user_id": "test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "risk_level" in data
    assert data["risk_level"] in ("low", "moderate", "high", "critical")
    assert "confidence" in data
    assert "modality_contributions" in data
    assert "key_findings" in data
    assert isinstance(data["key_findings"], list)
    assert "timestamp" in data


def test_assess_endpoint_empty_text():
    resp = client.post(
        "/api/assess/multimodal",
        data={"text": "   ", "user_id": "test"},
    )
    assert resp.status_code == 422


def test_assess_endpoint_missing_text():
    resp = client.post("/api/assess/multimodal", data={"user_id": "test"})
    assert resp.status_code == 422


def test_legacy_endpoint_alias():
    """Old /api/multimodal/analyze path should still work."""
    resp = client.post(
        "/api/multimodal/analyze",
        data={"text": "I feel okay today.", "user_id": "test"},
    )
    assert resp.status_code == 200


def test_assess_history():
    # First run an assessment to populate history
    client.post("/api/assess/multimodal", data={"text": "test text", "user_id": "history_test"})
    resp = client.get("/api/assessments/history_test")
    assert resp.status_code == 200
    data = resp.json()
    assert "assessments" in data
    assert data["total"] >= 1


def test_delete_user_data():
    uid = "delete_test_user"
    # Add data
    client.post("/api/assess/multimodal", data={"text": "some text", "user_id": uid})
    client.post("/api/phq8/score", json={"answers": [1, 1, 1, 1, 1, 1, 1, 1], "user_id": uid})
    # Delete
    resp = client.delete(f"/api/users/{uid}/data")
    assert resp.status_code == 200
    data = resp.json()
    assert data["assessments_deleted"] >= 1
    assert data["phq8_deleted"] >= 1
    # Verify empty
    history = client.get(f"/api/assessments/{uid}").json()
    assert history["total"] == 0
