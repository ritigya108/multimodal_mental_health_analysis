"""
Streamlit Assessment Page — mirrors the React Assessment page.
Sends text + optional audio/video to POST /api/assess/multimodal.
"""
import streamlit as st
import requests
import os
from datetime import datetime

st.set_page_config(page_title="Assessment", page_icon="🧠", layout="wide")

BACKEND_URL = (
    st.secrets.get("BACKEND_URL", None)
    or os.environ.get("BACKEND_URL", "http://localhost:8000")
)

# ── Crisis helpline ────────────────────────────────────────────────────────────
try:
    h = requests.get(f"{BACKEND_URL}/api/config/helpline", timeout=3).json()
    HELPLINE = f"{h.get('name', 'Tele-MANAS')} {h.get('number', '14416')}"
except Exception:
    HELPLINE = "Tele-MANAS 14416"

with st.sidebar:
    st.title("Assessment")
    st.caption("Multimodal depression screening")
    st.divider()
    st.markdown(f"**Crisis:** {HELPLINE}")
    st.caption("Free 24/7")

st.title("New assessment")
st.caption("Enter a text transcript and optionally upload audio or video.")

RISK_COLOR = {"low": "green", "moderate": "orange", "high": "red", "critical": "red"}

SAMPLE_TEXTS = [
    "I have been feeling very low and unmotivated for several weeks.",
    "Things have been okay. I've had some stressful days but mostly I feel fine.",
    "I feel completely hopeless. Nothing seems worth doing.",
]

with st.expander("Sample texts — click to use"):
    for i, s in enumerate(SAMPLE_TEXTS):
        if st.button(f"Sample {i+1}", key=f"sample_{i}"):
            st.session_state["assess_text"] = s

text = st.text_area(
    "Transcript *",
    value=st.session_state.get("assess_text", ""),
    height=180,
    placeholder="Describe how you have been feeling, or paste an interview transcript...",
    max_chars=5000,
    key="assess_text",
)

col_audio, col_video = st.columns(2)
with col_audio:
    audio_file = st.file_uploader("Audio file (optional)", type=["wav", "mp3", "webm", "ogg"])
with col_video:
    video_file = st.file_uploader("Video file (optional)", type=["mp4", "webm", "avi"])

st.divider()

if st.button("Run assessment", type="primary", disabled=not text.strip()):
    with st.spinner("Analysing…"):
        try:
            files = {}
            data  = {"text": text.strip(), "user_id": "streamlit_user"}

            if audio_file:
                files["audio_file"] = (audio_file.name, audio_file.getvalue(), audio_file.type)
            if video_file:
                files["video_file"] = (video_file.name, video_file.getvalue(), video_file.type)

            if files:
                resp = requests.post(f"{BACKEND_URL}/api/assess/multimodal", data=data, files=files, timeout=60)
            else:
                resp = requests.post(f"{BACKEND_URL}/api/assess/multimodal", data=data, timeout=60)

            resp.raise_for_status()
            result = resp.json()
            st.session_state["last_result"] = result

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend. Make sure it is running on port 8000.")
            st.stop()
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    # ── Display result ────────────────────────────────────────────────────────
    result = st.session_state["last_result"]
    risk   = result.get("risk_level", "unknown")
    color  = RISK_COLOR.get(risk, "gray")

    if risk in ("critical", "high"):
        st.warning(
            f"The screening indicates elevated distress. "
            f"If you are finding things difficult, please reach out: **{HELPLINE}** (free, 24/7)"
        )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Risk level",  f":{color}[{risk.upper()}]")
    col2.metric("Confidence",  f"{result.get('confidence', 0) * 100:.0f}%")
    col3.metric("PHQ-8 est.",  f"{result.get('phq8_estimate', '—')} / 24")
    col4.metric("Model",       "Neural" if not result.get("demo_mode") else "Heuristic")

    st.subheader("Modality contribution")
    contribs = result.get("modality_contributions", {})
    for mod in ("Text", "Audio", "Video"):
        val = contribs.get(mod.lower(), 0)
        st.progress(int(val), text=f"{mod}: {val:.1f}%")

    if result.get("key_findings"):
        st.subheader("Key findings")
        for f in result["key_findings"]:
            st.markdown(f"- {f}")

    if result.get("recommendations"):
        with st.expander("Recommendations"):
            for r in result["recommendations"][:6]:
                st.markdown(f"- {r}")

st.divider()
st.caption(f"This tool provides screening support and is not a medical diagnosis. Crisis: **{HELPLINE}**")
