"""
Bimodal Depression Screening — Streamlit Page
==============================================
Works today without training a model (heuristic fallback mode).
When a checkpoint is present (backend/checkpoints/eatd_fast/best.pt),
the backend automatically uses neural inference.
"""

import os
import streamlit as st
import plotly.graph_objects as go
import requests
from datetime import datetime

st.set_page_config(
    page_title="Bimodal Analysis",
    page_icon="🧠",
    layout="wide",
)

# ── Constants ──────────────────────────────────────────────────────────────────
BACKEND_URL = (
    st.secrets.get("BACKEND_URL", None)
    or os.environ.get("BACKEND_URL", "http://localhost:8000")
)

RISK_COLORS = {
    "low":      "#10b981",
    "moderate": "#f59e0b",
    "high":     "#ef4444",
    "critical": "#7c3aed",
}
RISK_EMOJIS = {
    "low":      "🟢",
    "moderate": "🟡",
    "high":     "🔴",
    "critical": "🚨",
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 Bimodal Analysis")
    st.caption("Depression screening using text and audio (EATD-Corpus).")

    st.divider()

    st.markdown("### 📡 Backend Status")
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if r.status_code == 200:
            st.success("✅ Backend online")
        else:
            st.warning("⚠️ Backend returned non-200")
    except Exception:
        st.error("❌ Backend offline\nStart it with:\n```\npython backend/main.py\n```")

    st.divider()

    st.error("**🚨 Crisis Support (India)**")
    st.markdown("**KIRAN: 1800-599-0019** (free, 24/7)")
    st.markdown("**iCall: 9152987821**")
    st.markdown("**Vandrevala: 1860-2662-345**")

    st.divider()
    st.caption(
        "ℹ️ This tool uses a linguistic heuristic when no trained model is "
        "available. Train on EATD-Corpus and connect the checkpoint for neural inference."
    )

# ── Main content ───────────────────────────────────────────────────────────────
st.title("Bimodal Depression Screening")
st.markdown(
    "Submit a **text transcript** (required) and optionally an **audio** file. "
    "The system combines both modalities to assess mental health indicators."
)

st.info(
    "**How it works in demo mode:**  \n"
    "The backend uses linguistic feature extraction (first-person pronoun rate, "
    "negative/positive vocabulary ratio, crisis keyword detection) to produce a risk assessment. "
    "Train on the EATD-Corpus and the page will automatically switch to neural inference — "
    "**no frontend changes needed**.",
    icon="ℹ️",
)

st.divider()

# ── Input form ─────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📝 Transcript / Text")
    sample_texts = {
        "Select a sample…": "",
        "Low risk (positive)": (
            "Today was actually a good day. I went for a walk in the morning and felt "
            "peaceful. I am grateful for my family and feeling motivated about my goals. "
            "Things are going well and I feel calm and content."
        ),
        "Moderate risk": (
            "I have been feeling a bit stressed and worried lately. Work has been difficult "
            "and I am tired most of the time. I sometimes feel alone and it is hard to "
            "concentrate. I hope things get better soon."
        ),
        "High risk": (
            "Everything feels hopeless. I am exhausted all the time and nothing seems "
            "worthwhile. I feel empty inside and I cannot stop crying. I am worthless "
            "and nobody would notice if I disappeared. I just want the pain to stop."
        ),
        "Critical risk": (
            "I want to die. I have been thinking about suicide for weeks. "
            "I feel there is no reason to live and I am better off dead. "
            "I cannot take it anymore. I have lost all hope."
        ),
    }
    sample_choice = st.selectbox("Load a sample text (optional)", list(sample_texts.keys()))

    default_text = sample_texts[sample_choice]
    transcript = st.text_area(
        "Enter text transcript here",
        value=default_text,
        height=220,
        placeholder=(
            "Paste a conversation transcript, journal entry, or any text here…\n\n"
            "Example: 'I have been feeling really down lately. Everything seems overwhelming "
            "and I can't find the energy to do things I used to enjoy.'"
        ),
    )
    char_count = len(transcript)
    word_count = len(transcript.split()) if transcript.strip() else 0
    st.caption(f"{word_count} words · {char_count} characters")

with col_right:
    st.subheader("🎵 Audio (optional)")
    audio_file = st.file_uploader(
        "Upload audio file",
        type=["wav", "mp3", "m4a", "flac", "ogg"],
        help="Supported: WAV, MP3, M4A, FLAC, OGG. Max 200 MB.",
    )
    if audio_file:
        st.audio(audio_file)
        st.success(f"✅ {audio_file.name}")

video_file = None

st.divider()

# ── Run analysis ───────────────────────────────────────────────────────────────
run_btn = st.button(
    "🚀 Run Analysis",
    type="primary",
    use_container_width=True,
    disabled=not transcript.strip(),
)

if not transcript.strip():
    st.caption("⬆️ Enter some text above to enable analysis.")

# ── Results ────────────────────────────────────────────────────────────────────
if run_btn and transcript.strip():
    with st.spinner("Analysing… (combining text and audio modalities)"):
        try:
            files = {}
            if audio_file:
                audio_file.seek(0)
                files["audio_file"] = (audio_file.name, audio_file, audio_file.type or "audio/wav")

            data = {"text": transcript.strip(), "user_id": "streamlit_user"}

            response = requests.post(
                f"{BACKEND_URL}/api/multimodal/analyze",
                data=data,
                files=files if files else None,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()

        except requests.exceptions.ConnectionError:
            st.error(
                "❌ Cannot connect to backend.  \n"
                "Start it with: `cd multimodal_mental_health_analysis/backend && python main.py`"
            )
            st.stop()
        except requests.exceptions.HTTPError as e:
            st.error(f"❌ Backend error: {e.response.text}")
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.stop()

    # ── Store in session state ─────────────────────────────────────────────────
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    st.session_state.analysis_history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "result": result,
        "text_preview": transcript[:80] + ("…" if len(transcript) > 80 else ""),
    })

    # ── Results display ────────────────────────────────────────────────────────
    risk = result.get("risk_level", "low")
    dep_prob = result.get("depression_probability", 0.0)
    phq8 = result.get("phq8_estimate", 0.0)
    model_used = result.get("model_used", "heuristic")
    note = result.get("note", "")

    st.success("✅ Analysis complete!")

    # ── Crisis banner ──────────────────────────────────────────────────────────
    crisis = result.get("crisis_flags", {})
    if crisis.get("high_risk_detected"):
        st.error(
            "🚨 **CRITICAL: Potential crisis detected.**  \n"
            "Please contact a mental health professional immediately.  \n"
            "**KIRAN: 1800-599-0019 (India, free, 24/7)**  |  "
            "iCall: 9152987821  |  Vandrevala: 1860-2662-345"
        )
    elif crisis.get("medium_risk_detected"):
        st.warning(
            "⚠️ **Elevated distress signals detected.**  \n"
            "Consider reaching out to a mental health professional.  \n"
            "KIRAN: 1800-599-0019 (free, 24/7)"
        )

    # ── Top metrics row ────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)

    with m1:
        risk_color = RISK_COLORS[risk]
        st.markdown(
            f"""<div style="background:{risk_color}22;border-left:4px solid {risk_color};
            padding:1rem;border-radius:0.5rem;">
            <p style="margin:0;font-size:0.85rem;color:{risk_color};font-weight:600;">RISK LEVEL</p>
            <h2 style="margin:0;color:{risk_color};">{RISK_EMOJIS[risk]} {risk.upper()}</h2>
            </div>""",
            unsafe_allow_html=True,
        )

    with m2:
        st.metric("Depression Probability", f"{dep_prob * 100:.1f}%", help="0% = no risk, 100% = high risk")

    with m3:
        st.metric("SDS-score estimate", f"{phq8} / 24", help="Score >= 10 indicates moderate-severe")

    with m4:
        label = "Depressed" if result.get("binary_prediction", 0) else "Not Depressed"
        icon  = "🔴" if result.get("binary_prediction", 0) else "🟢"
        st.metric("Binary Classification", f"{icon} {label}")

    st.caption(
        f"Model: **{model_used}** · "
        f"Modalities: text{'  + audio' if audio_file else ''} · "
        f"{note}"
    )

    st.divider()

    # ── Charts row ─────────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🎯 Modality Contribution")
        mw = result.get("modality_weights", {})
        labels = [k.title() for k, v in mw.items() if v > 0]
        values = [v for v in mw.values() if v > 0]

        if labels:
            fig_pie = go.Figure(go.Pie(
                labels=labels,
                values=values,
                hole=0.45,
                marker_colors=["#6366f1", "#10b981"],
            ))
            fig_pie.update_layout(
                margin=dict(l=0, r=0, t=20, b=0),
                height=260,
                showlegend=True,
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No modality weight data available.")

    with c2:
        st.subheader("📊 Risk Score Gauge")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=dep_prob * 100,
            number={"suffix": "%", "font": {"size": 28}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": RISK_COLORS[risk]},
                "steps": [
                    {"range": [0, 30],  "color": "#d1fae5"},
                    {"range": [30, 50], "color": "#fef3c7"},
                    {"range": [50, 70], "color": "#fee2e2"},
                    {"range": [70, 100], "color": "#ede9fe"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 3},
                    "thickness": 0.75,
                    "value": dep_prob * 100,
                },
            },
        ))
        fig_gauge.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=0))
        st.plotly_chart(fig_gauge, use_container_width=True)

    st.divider()

    # ── Linguistic features ────────────────────────────────────────────────────
    lf = result.get("linguistic_features", {})
    if lf:
        st.subheader("🔬 Linguistic Features")
        lf1, lf2, lf3, lf4 = st.columns(4)
        lf1.metric("Word Count",         lf.get("word_count", "—"))
        lf2.metric("First-Person Rate",  f"{lf.get('first_person_ratio', 0)*100:.1f}%",
                   help="High first-person pronoun use correlates with depression")
        lf3.metric("Negative Word Rate", f"{lf.get('negative_word_ratio', 0)*100:.1f}%")
        lf4.metric("Positive Word Rate", f"{lf.get('positive_word_ratio', 0)*100:.1f}%")
        st.divider()

    # ── Recommendations ────────────────────────────────────────────────────────
    recs = result.get("recommendations", [])
    if recs:
        st.subheader("💡 Personalised Recommendations")
        for rec in recs:
            st.markdown(f"- {rec}")

    st.divider()

    # ── Raw JSON (collapsible) ─────────────────────────────────────────────────
    with st.expander("🔧 View raw API response (for debugging)"):
        st.json(result)


# ── Analysis history ───────────────────────────────────────────────────────────
if "analysis_history" in st.session_state and st.session_state.analysis_history:
    st.divider()
    st.subheader("📋 Session History")
    for i, h in enumerate(reversed(st.session_state.analysis_history[-5:]), 1):
        r = h["result"]
        risk_h = r.get("risk_level", "low")
        col_a, col_b, col_c = st.columns([3, 1, 1])
        col_a.markdown(f"**{i}.** {h['text_preview']}")
        col_b.markdown(f"{RISK_EMOJIS[risk_h]} **{risk_h.upper()}**")
        col_c.caption(h["timestamp"])


# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "⚠️ **Disclaimer:** This tool is for research and support purposes only. "
    "It is NOT a substitute for professional mental health diagnosis or treatment. "
    "Always consult a qualified mental health professional."
)
st.caption(
    "🚨 **Emergency (India):** KIRAN 1800-599-0019 · iCall 9152987821 · "
    "Vandrevala 1860-2662-345 · Police 100"
)
