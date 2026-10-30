"""
Streamlit Home — MindCare overview dashboard (updated).
Mood Tracker removed; shows assessment history, risk level, and quick links.
"""
import streamlit as st
import requests
import os
from datetime import datetime

st.set_page_config(
    page_title="MindCare — Overview",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = (
    st.secrets.get("BACKEND_URL", None)
    or os.environ.get("BACKEND_URL", "http://localhost:8000")
)

# ── Crisis helpline ────────────────────────────────────────────────────────────
try:
    helpline = requests.get(f"{BACKEND_URL}/api/config/helpline", timeout=3).json()
    HELPLINE_NUMBER = helpline.get("number", "14416")
    HELPLINE_NAME   = helpline.get("name", "Tele-MANAS")
except Exception:
    HELPLINE_NUMBER = "14416"
    HELPLINE_NAME   = "Tele-MANAS"

# ── Session state ──────────────────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = "streamlit_user"

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("MindCare")
    st.caption("Multimodal Mental Health Analysis")
    st.divider()
    st.markdown(f"**{HELPLINE_NAME}:** `{HELPLINE_NUMBER}`")
    st.caption("Free 24/7 crisis support")

# ── Main content ───────────────────────────────────────────────────────────────
st.title("Overview")
st.caption(datetime.now().strftime("%A, %d %B %Y"))

# Try to load recent assessments from backend
try:
    hist = requests.get(
        f"{BACKEND_URL}/api/assessments/{st.session_state.user_id}",
        params={"page": 1, "page_size": 5},
        timeout=5,
    ).json()
    assessments = hist.get("assessments", [])
    total = hist.get("total", 0)
except Exception:
    assessments = []
    total = 0

latest = assessments[0] if assessments else None

# ── KPI row ────────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Current risk level", latest.get("risk_level", "N/A").title() if latest else "No data")

with col2:
    conf = latest.get("confidence") if latest else None
    st.metric("Confidence", f"{conf * 100:.0f}%" if conf is not None else "—")

with col3:
    st.metric("Assessments completed", total)

with col4:
    if len(assessments) >= 2:
        prev = assessments[1].get("risk_level", "")
        cur  = latest.get("risk_level", "") if latest else ""
        order = {"low": 0, "moderate": 1, "high": 2, "critical": 3}
        delta = order.get(cur, 0) - order.get(prev, 0)
        label = "Improved" if delta < 0 else "Worsened" if delta > 0 else "Stable"
        st.metric("Since last assessment", label)
    else:
        st.metric("Since last assessment", "—")

st.divider()

# ── Risk level indicator ───────────────────────────────────────────────────────
if latest:
    risk = latest.get("risk_level", "unknown")
    RISK_COLOR = {"low": "green", "moderate": "orange", "high": "red", "critical": "red"}
    color = RISK_COLOR.get(risk, "gray")
    st.markdown(f"### Risk level: :{color}[{risk.upper()}]")

    # Modality bars
    st.subheader("Modality contribution")
    contribs = latest.get("modality_contributions", {})
    for mod in ("Text", "Audio"):
        val = contribs.get(mod.lower(), 0)
        st.progress(int(val), text=f"{mod}: {val:.1f}%")

    # Key findings
    if latest.get("key_findings"):
        st.subheader("Key findings")
        for finding in latest["key_findings"]:
            st.markdown(f"- {finding}")
else:
    st.info("No assessments yet. Use the **Assessment** page to run your first screening.")

st.divider()

# ── Quick navigation ───────────────────────────────────────────────────────────
st.subheader("Quick actions")
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.page_link("pages/1_Assessment.py", label="Run new assessment", icon="🧠")
with col_b:
    st.page_link("pages/2_PHQ8.py", label="PHQ-8 questionnaire", icon="📋")
with col_c:
    st.page_link("pages/3_AI_Chat.py", label="AI Chat", icon="💬")

# ── Disclaimer + helpline footer ──────────────────────────────────────────────
st.divider()
st.caption(
    f"This tool provides screening support and is not a medical diagnosis. "
    f"Crisis support: **{HELPLINE_NAME} {HELPLINE_NUMBER}** (free, 24/7)"
)
