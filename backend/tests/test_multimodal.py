"""
tests/test_multimodal.py - Legacy endpoint compatibility tests.

These tests cover the same routes as before the EATD 3-question rewrite,
now using the correct field names (positive_text instead of text).

Run from backend/:
    set PYTHONPATH and then: python -m pytest tests/ -v
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from fastapi.testclient import TestClient
from main import app, _score_text_heuristic

client = TestClient(app)


# ── _score_text_heuristic unit tests ─────────────────────────────────────────

def test_score_heuristic_low_risk():
    result = _score_text_heuristic("I feel great today. Everything is going well.")
    assert result["depression_score"] < 0.5
    assert "neg_ratio" in result
    assert "pos_ratio" in result
    assert result["crisis_high"] is False


def test_score_heuristic_high_risk_crisis():
    result = _score_text_heuristic("I want to kill myself and end my life.")
    assert result["crisis_high"] is True
    assert result["depression_score"] > 0.5


def test_score_heuristic_moderate_risk():
    result = _score_text_heuristic("I feel sad and tired most days. Things are difficult.")
    assert 0.1 <= result["depression_score"] <= 1.0


def test_score_heuristic_text_only_no_crisis():
    result = _score_text_heuristic("Neutral text here.")
    assert result["crisis_high"] is False
    assert result["crisis_mid"] is False


def test_score_heuristic_chinese_neg_chars():
    """Chinese depression characters should increase the score."""
    result_cn  = _score_text_heuristic("我感到绝望和孤独。")   # hopeless and lonely
    result_ok  = _score_text_heuristic("我感到幸福快乐。")     # happy
    assert result_cn["depression_score"] >= result_ok["depression_score"]


# ── Endpoint tests ────────────────────────────────────────────────────────────

def test_assess_endpoint_positive_text_only():
    resp = client.post(
        "/api/assess/multimodal",
        data={"positive_text": "I have been feeling hopeless and sad for weeks."},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "risk_level" in data
    assert data["risk_level"] in ("low", "moderate", "elevated", "high", "critical")
    assert "confidence" in data
    assert "modality_contributions" in data
    assert "key_findings" in data
    assert isinstance(data["key_findings"], list)
    assert "timestamp" in data


def test_assess_endpoint_all_three_questions():
    resp = client.post(
        "/api/assess/multimodal",
        data={
            "positive_text": "I felt happy when I was with my family.",
            "neutral_text":  "I wake up at 7am and go to work.",
            "negative_text": "I have been feeling sad and tired recently.",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["per_question_scores"]) == 3
    keys = {q["question"] for q in data["per_question_scores"]}
    assert keys == {"positive", "neutral", "negative"}


def test_assess_endpoint_empty_all_text_returns_422():
    resp = client.post(
        "/api/assess/multimodal",
        data={"positive_text": "   ", "neutral_text": "", "negative_text": ""},
    )
    assert resp.status_code == 422


def test_assess_endpoint_missing_all_text_returns_422():
    resp = client.post("/api/assess/multimodal", data={})
    assert resp.status_code == 422


def test_legacy_endpoint_alias():
    """Old /api/multimodal/analyze path must still return 200."""
    resp = client.post(
        "/api/multimodal/analyze",
        data={"text": "I feel okay today."},
    )
    assert resp.status_code == 200


def test_assess_history():
    """Run an assessment then verify it appears in history."""
    client.post(
        "/api/assess/multimodal",
        data={"positive_text": "test text for history"},
    )
    resp = client.get("/api/assessments/anonymous")
    assert resp.status_code == 200
    data = resp.json()
    assert "assessments" in data
    assert data["total"] >= 1


def test_delete_user_data():
    uid = "delete_test_legacy"
    # Add an assessment
    client.post(
        "/api/assess/multimodal",
        data={"positive_text": "some text", "neutral_text": "", "negative_text": ""},
    )
    client.post("/api/phq8/score", json={"answers": [1, 1, 1, 1, 1, 1, 1, 1], "user_id": uid})
    # Delete
    resp = client.delete(f"/api/users/{uid}/data")
    assert resp.status_code == 200
    data = resp.json()
    assert "phq8_deleted" in data
