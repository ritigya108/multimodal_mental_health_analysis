import streamlit as st
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Mood Tracker", page_icon="ðŸ˜Š", layout="wide")

st.title("Mood Tracker ðŸ˜Š")
st.markdown("### How are you feeling today?")

# Mood selection
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Rate Your Mood")
    
    mood_score = st.slider(
        "Select your mood (1-10)",
        min_value=1,
        max_value=10,
        value=5,
        help="1 = Very Bad, 10 = Amazing"
    )
    
    # Emoji display based on mood
    mood_emojis = {
        1: "ðŸ˜¢", 2: "ðŸ˜Ÿ", 3: "ðŸ˜•", 4: "ðŸ˜", 5: "ðŸ˜Š",
        6: "ðŸ™‚", 7: "ðŸ˜ƒ", 8: "ðŸ˜„", 9: "ðŸ˜", 10: "ðŸ¤©"
    }
    
    mood_labels = {
        1: "Very Bad", 2: "Bad", 3: "Poor", 4: "Below Average", 5: "Neutral",
        6: "Okay", 7: "Good", 8: "Great", 9: "Excellent", 10: "Amazing"
    }
    
    st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background-color: #f0f2f6; border-radius: 1rem; margin: 1rem 0;">
            <div style="font-size: 5rem;">{mood_emojis[mood_score]}</div>
            <h2>{mood_labels[mood_score]}</h2>
            <h1 style="color: #6366f1;">{mood_score}/10</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Notes
    notes = st.text_area(
        "What's on your mind? (Optional)",
        placeholder="Share your thoughts, feelings, or what influenced your mood today...",
        height=150
    )
    
    # Submit button
    if st.button("Log Mood", type="primary", use_container_width=True):
        # Save mood log
        if 'mood_logs' not in st.session_state:
            st.session_state.mood_logs = []
        
        st.session_state.mood_logs.append({
            'date': datetime.now(),
            'score': mood_score,
            'notes': notes
        })
        
        st.success("âœ… Mood logged successfully!")
        st.balloons()

with col2:
    st.subheader("ðŸ’¡ Mood Tracking Tips")
    
    st.info("""
    **Be Honest**
    
    There's no right or wrong answer. Track how you truly feel.
    """)
    
    st.success("""
    **Track Regularly**
    
    Daily tracking helps identify patterns and triggers.
    """)
    
    st.warning("""
    **Add Context**
    
    Notes help you understand what affects your mood.
    """)
    
    st.info("""
    **Review Trends**
    
    Check your dashboard to see mood patterns over time.
    """)
    
    st.error("""
    **Feeling Low?**
    
    It's okay to not be okay. Consider talking to someone.
    """)
    
    if st.button("ðŸ’¬ Chat with AI", use_container_width=True):
        st.switch_page("pages/3_AI_Chat.py")

st.divider()

# Quick mood selection
st.subheader("Quick Select")

cols = st.columns(10)
for i, col in enumerate(cols, 1):
    with col:
        if st.button(f"{mood_emojis[i]}\n{i}", key=f"quick_{i}", use_container_width=True):
            st.session_state.quick_mood = i
            st.rerun()

st.divider()

# Mood history
st.subheader("ðŸ“Š Your Mood History")

if 'mood_logs' in st.session_state and st.session_state.mood_logs:
    df = pd.DataFrame(st.session_state.mood_logs)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M')
    st.dataframe(
        df[['date', 'score', 'notes']].rename(columns={
            'date': 'Date & Time',
            'score': 'Mood Score',
            'notes': 'Notes'
        }),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No mood logs yet. Start tracking your mood above!")

st.divider()
st.caption("ðŸ’™ Your mental health matters. Keep tracking to understand your patterns better.")
