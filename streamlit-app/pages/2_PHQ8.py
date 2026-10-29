"""
Streamlit PHQ-8 Page — 8-question PHQ questionnaire with scoring.
"""
import streamlit as st
import requests
import os

st.set_page_config(page_title="PHQ-8", page_icon="📋", layout="centered")

BACKEND_URL = (
    st.secrets.get("BACKEND_URL", None)
    or os.environ.get("BACKEND_URL", "http://localhost:8000")
)

try:
    h = requests.get(f"{BACKEND_URL}/api/config/helpline", timeout=3).json()
    HELPLINE = f"{h.get('name', 'Tele-MANAS')} {h.get('number', '14416')}"
except Exception:
    HELPLINE = "Tele-MANAS 14416"

with st.sidebar:
    st.title("PHQ-8")
    st.caption("Patient Health Questionnaire")
    st.divider()
    st.markdown(f"**Crisis:** {HELPLINE}")

st.title("PHQ-8 questionnaire")
st.caption("Over the last 2 weeks, how often have you been bothered by the following problems?")

QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself — or that you are a failure",
    "Trouble concentrating on things",
    "Moving or speaking so slowly, or being fidgety or restless",
]

SCALE_OPTIONS = ["Not at all (0)", "Several days (1)", "More than half the days (2)", "Nearly every day (3)"]

answers = []
for i, q in enumerate(QUESTIONS):
    val = st.radio(
        f"**{i+1}.** {q}",
        options=SCALE_OPTIONS,
        index=None,
        key=f"phq8_q{i}",
    )
    answers.append(SCALE_OPTIONS.index(val) if val is not None else None)

answered = sum(1 for a in answers if a is not None)
st.progress(answered / 8, text=f"{answered} of 8 answered")

st.divider()

if st.button("Submit questionnaire", type="primary", disabled=answered < 8):
    int_answers = [int(a) for a in answers]
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/phq8/score",
            json={"answers": int_answers, "user_id": "streamlit_user"},
            timeout=10,
        )
        resp.raise_for_status()
        result = resp.json()
    except Exception as e:
        st.error(f"Scoring failed: {e}")
        st.stop()

    score    = result["score"]
    severity = result["severity"]
    desc     = result["severity_description"]

    SEVERITY_COLOR = {
        "Minimal": "green", "Mild": "blue",
        "Moderate": "orange", "Moderately Severe": "red", "Severe": "red",
    }
    color = SEVERITY_COLOR.get(severity, "gray")

    st.subheader("Results")
    col1, col2 = st.columns(2)
    col1.metric("Total score", f"{score} / 24")
    col2.metric("Severity", f":{color}[{severity}]")
    st.info(desc)

    # Comparison with last model assessment
    last = st.session_state.get("last_result")
    if last:
        model_risk = last.get("risk_level", "")
        order = {"low": 0, "moderate": 1, "high": 2, "critical": 3}
        severity_order = {"Minimal": 0, "Mild": 1, "Moderate": 2, "Moderately Severe": 3, "Severe": 4}
        m_idx = order.get(model_risk, 0)
        p_idx = severity_order.get(severity, 0)
        diff = abs(m_idx - (p_idx // 1))
        if diff == 0:
            agreement = "Agreement"
        elif diff <= 1:
            agreement = "Partial agreement"
        else:
            agreement = "Disagreement"
        st.markdown(f"**Model vs PHQ-8:** Model predicted **{model_risk}**, PHQ-8 shows **{severity}** → _{agreement}_")

st.divider()
st.caption(f"The PHQ-8 is a validated screening tool, not a clinical diagnosis. Crisis: **{HELPLINE}**")
