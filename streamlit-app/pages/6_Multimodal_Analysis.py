"""
Multimodal Mental Health Analysis â€” Streamlit Page
====================================================
Works TODAY without the DAIC-WOZ dataset.
When a trained model checkpoint is present (backend/checkpoints/daic/best.pt),
the backend automatically uses it for neural inference.
"""

import os
import streamlit as st
import plotly.graph_objects as go
import requests
import json
from datetime import datetime

st.set_page_config(
    page_title="Multimodal Analysis",
    page_icon="ðŸ§ ",
    layout="wide",
)

# â”€â”€ Constants â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Resolution order:
#   1. st.secrets["BACKEND_URL"]   (Streamlit Cloud secrets)
#   2. BACKEND_URL env var          (Docker / local env)
#   3. localhost fallback           (local dev without backend container)
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
    "low":      "ðŸŸ¢",
    "moderate": "ðŸŸ¡",
    "high":     "ðŸ”´",
    "critical": "ðŸš¨",
}

# â”€â”€ Sidebar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with st.sidebar:
    st.markdown("## ðŸ§  Multimodal Analysis")
    st.caption("AI-powered mental health assessment using text, audio, and video.")

    st.divider()

    st.markdown("### ðŸ“¡ Backend Status")
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if r.status_code == 200:
            st.success("âœ… Backend online")
        else:
            st.warning("âš ï¸ Backend returned non-200")
    except Exception:
        st.error("âŒ Backend offline\nStart it with:\n```\npython backend/main.py\n```")

    st.divider()

    st.error("**ðŸš¨ Crisis Support (India)**")
    st.markdown("**KIRAN: 1800-599-0019** (free, 24/7)")
    st.markdown("**iCall: 9152987821**")
    st.markdown("**Vandrevala: 1860-2662-345**")

    st.divider()
    st.caption(
        "â„¹ï¸ This tool uses a linguistic heuristic when no trained model is "
        "available. Connect the backend to a trained checkpoint for neural inference."
    )

# â”€â”€ Main content â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.title("ðŸŽ­ Multimodal Mental Health Analysis")
st.markdown(
    "Submit a **text transcript** (required) and optionally an **audio** or **video** file. "
    "The system combines all available modalities to assess mental health indicators."
)

st.info(
    "**How it works without the DAIC-WOZ dataset:**  \n"
    "The backend uses advanced linguistic feature extraction (first-person pronoun rate, "
    "negative/positive vocabulary ratio, crisis keyword detection) to produce a risk assessment. "
    "Once you train on DAIC-WOZ, the same page automatically switches to neural inference â€” "
    "**no frontend changes needed**.",
    icon="â„¹ï¸",
)

st.divider()

# â”€â”€ Input form â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("ðŸ“ Transcript / Text")
    sample_texts = {
        "Select a sampleâ€¦": "",
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
            "Paste a conversation transcript, journal entry, or any text hereâ€¦\n\n"
            "Example: 'I have been feeling really down lately. Everything seems overwhelming "
            "and I can't find the energy to do things I used to enjoy.'"
        ),
    )
    char_count = len(transcript)
    word_count = len(transcript.split()) if transcript.strip() else 0
    st.caption(f"{word_count} words Â· {char_count} characters")

with col_right:
    st.subheader("ðŸŽµ Audio (optional)")
    audio_file = st.file_uploader(
        "Upload audio file",
        type=["wav", "mp3", "m4a", "flac", "ogg"],
        help="Supported: WAV, MP3, M4A, FLAC, OGG. Max 200 MB.",
    )
    if audio_file:
        st.audio(audio_file)
        st.success(f"âœ… {audio_file.name}")

    st.subheader("ðŸŽ¥ Video (optional)")
    video_file = st.file_uploader(
        "Upload video file",
        type=["mp4", "avi", "mov", "mkv"],
        help="Facial expression analysis requires OpenFace (available after dataset setup).",
    )
    if video_file:
        st.video(video_file)
        st.success(f"âœ… {video_file.name}")

    if video_file and not audio_file:
        st.info("ðŸ’¡ Tip: Upload the matching audio file alongside the video for better results.")

st.divider()

# â”€â”€ Run analysis â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
run_btn = st.button(
    "ðŸš€ Run Multimodal Analysis",
    type="primary",
    use_container_width=True,
    disabled=not transcript.strip(),
)

if not transcript.strip():
    st.caption("â¬†ï¸ Enter some text above to enable analysis.")

# â”€â”€ Results â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if run_btn and transcript.strip():
    with st.spinner("Analysingâ€¦ (combining text, audio, and video modalities)"):
        try:
            # Build multipart form data
            files = {}
            if audio_file:
                audio_file.seek(0)
                files["audio_file"] = (audio_file.name, audio_file, audio_file.type or "audio/wav")
            if video_file:
                video_file.seek(0)
                files["video_file"] = (video_file.name, video_file, video_file.type or "video/mp4")

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
                "âŒ Cannot connect to backend.  \n"
                "Start it with: `cd multimodal_mental_health_analysis/backend && python main.py`"
            )
            st.stop()
        except requests.exceptions.HTTPError as e:
            st.error(f"âŒ Backend error: {e.response.text}")
            st.stop()
        except Exception as e:
            st.error(f"âŒ Unexpected error: {e}")
            st.stop()

    # â”€â”€ Store in session state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if "analysis_history" not in st.session_state:
        st.session_state.analysis_history = []
    st.session_state.analysis_history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "result": result,
        "text_preview": transcript[:80] + ("â€¦" if len(transcript) > 80 else ""),
    })

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # RESULTS DISPLAY
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    risk = result.get("risk_level", "low")
    dep_prob = result.get("depression_probability", 0.0)
    phq8 = result.get("phq8_estimate", 0.0)
    model_used = result.get("model_used", "heuristic")
    note = result.get("note", "")

    st.success("âœ… Analysis complete!")

    # â”€â”€ Crisis banner (always shown first) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    crisis = result.get("crisis_flags", {})
    if crisis.get("high_risk_detected"):
        st.error(
            "ðŸš¨ **CRITICAL: Potential crisis detected.**  \n"
            "Please contact a mental health professional immediately.  \n"
            "**KIRAN: 1800-599-0019 (India, free, 24/7)**  |  "
            "iCall: 9152987821  |  Vandrevala: 1860-2662-345"
        )
    elif crisis.get("medium_risk_detected"):
        st.warning(
            "âš ï¸ **Elevated distress signals detected.**  \n"
            "Consider reaching out to a mental health professional.  \n"
            "KIRAN: 1800-599-0019 (free, 24/7)"
        )

    # â”€â”€ Top metrics row â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
        st.metric("PHQ-8 Estimate", f"{phq8} / 24", help="PHQ-8 â‰¥10 = moderateâ€“severe depression")

    with m4:
        label = "Depressed" if result.get("binary_prediction", 0) else "Not Depressed"
        icon  = "ðŸ”´" if result.get("binary_prediction", 0) else "ðŸŸ¢"
        st.metric("Binary Classification", f"{icon} {label}")

    st.caption(
        f"Model: **{model_used}** Â· "
        f"Modalities used: text{'  + audio' if audio_file else ''}{'  + video' if video_file else ''} Â· "
        f"{note}"
    )

    st.divider()

    # â”€â”€ Charts row â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("ðŸŽ¯ Modality Contribution")
        mw = result.get("modality_weights", {})
        labels = [k.title() for k, v in mw.items() if v > 0]
        values = [v for v in mw.values() if v > 0]

        if labels:
            fig_pie = go.Figure(go.Pie(
                labels=labels,
                values=values,
                hole=0.45,
                marker_colors=["#6366f1", "#10b981", "#f59e0b"],
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
        st.subheader("ðŸ“Š Risk Score Gauge")
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
                    {"range": [70, 100],"color": "#ede9fe"},
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

    # â”€â”€ Linguistic features â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    lf = result.get("linguistic_features", {})
    if lf:
        st.subheader("ðŸ”¬ Linguistic Features")
        lf1, lf2, lf3, lf4 = st.columns(4)
        lf1.metric("Word Count",          lf.get("word_count", "â€”"))
        lf2.metric("First-Person Rate",   f"{lf.get('first_person_ratio', 0)*100:.1f}%",
                   help="High first-person pronoun use correlates with depression")
        lf3.metric("Negative Word Rate",  f"{lf.get('negative_word_ratio', 0)*100:.1f}%")
        lf4.metric("Positive Word Rate",  f"{lf.get('positive_word_ratio', 0)*100:.1f}%")
        st.divider()

    # â”€â”€ Recommendations â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    recs = result.get("recommendations", [])
    if recs:
        st.subheader("ðŸ’¡ Personalised Recommendations")
        for rec in recs:
            if rec.startswith("âš ï¸"):
                st.error(rec)
            else:
                st.markdown(f"- {rec}")

    st.divider()

    # â”€â”€ Raw JSON (collapsible) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    with st.expander("ðŸ”§ View raw API response (for debugging)"):
        st.json(result)


# â”€â”€ Analysis history â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if "analysis_history" in st.session_state and st.session_state.analysis_history:
    st.divider()
    st.subheader("ðŸ“‹ Session History")
    for i, h in enumerate(reversed(st.session_state.analysis_history[-5:]), 1):
        r = h["result"]
        risk_h = r.get("risk_level", "low")
        col_a, col_b, col_c = st.columns([3, 1, 1])
        col_a.markdown(f"**{i}.** {h['text_preview']}")
        col_b.markdown(f"{RISK_EMOJIS[risk_h]} **{risk_h.upper()}**")
        col_c.caption(h["timestamp"])


# â”€â”€ Footer â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.divider()
st.caption(
    "âš ï¸ **Disclaimer:** This tool is for research and support purposes only. "
    "It is NOT a substitute for professional mental health diagnosis or treatment. "
    "Always consult a qualified mental health professional."
)
st.caption(
    "ðŸš¨ **Emergency (India):** KIRAN 1800-599-0019 Â· iCall 9152987821 Â· "
    "Vandrevala 1860-2662-345 Â· Police 100"
)
