import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Journal", page_icon="ðŸ“", layout="wide")

# Try to import sentiment analyzers with better error handling
SENTIMENT_AVAILABLE = False
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
    SENTIMENT_AVAILABLE = True
except Exception as e:
    st.sidebar.warning(f"âš ï¸ Advanced sentiment analysis unavailable. Using simple analysis. Error: {str(e)[:50]}")

st.title("My Journal ðŸ“")
st.markdown("### Write your thoughts and feelings")

# Initialize session state
if 'journal_entries' not in st.session_state:
    st.session_state.journal_entries = []

if 'clear_input' not in st.session_state:
    st.session_state.clear_input = False

def simple_sentiment_analysis(text):
    """Simple keyword-based sentiment analysis"""
    text_lower = text.lower()
    
    positive_words = ['good', 'great', 'happy', 'excellent', 'wonderful', 'amazing', 
                     'love', 'joy', 'excited', 'grateful', 'blessed', 'fantastic',
                     'awesome', 'brilliant', 'perfect', 'beautiful', 'peaceful']
    
    negative_words = ['bad', 'sad', 'terrible', 'awful', 'hate', 'angry', 
                     'depressed', 'anxious', 'worried', 'stressed', 'upset',
                     'horrible', 'miserable', 'frustrated', 'disappointed', 'lonely']
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    total = pos_count + neg_count
    if total == 0:
        return 0.0
    
    score = (pos_count - neg_count) / total
    return score

def analyze_text_sentiment(text):
    """Analyze sentiment using available method"""
    if SENTIMENT_AVAILABLE:
        try:
            vader_scores = analyzer.polarity_scores(text)
            return vader_scores['compound']
        except Exception:
            return simple_sentiment_analysis(text)
    else:
        return simple_sentiment_analysis(text)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("âœï¸ New Entry")
    
    # Journal entry input
    if st.session_state.clear_input:
        default_value = ""
        st.session_state.clear_input = False
    else:
        default_value = st.session_state.get("temp_journal_text", "")
    
    entry_text = st.text_area(
        "What's on your mind?",
        placeholder="Write your thoughts, feelings, and experiences here... Be honest and open with yourself.",
        height=300,
        value=default_value,
        key="journal_text_input"
    )
    
    # Store temporarily
    st.session_state.temp_journal_text = entry_text
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("ðŸ’¾ Save Entry", type="primary", use_container_width=True):
            if entry_text and entry_text.strip():
                # Analyze sentiment
                sentiment_score = analyze_text_sentiment(entry_text)
                
                if sentiment_score >= 0.05:
                    sentiment = "Positive"
                    emoji = "ðŸ˜Š"
                elif sentiment_score <= -0.05:
                    sentiment = "Negative"
                    emoji = "ðŸ˜”"
                else:
                    sentiment = "Neutral"
                    emoji = "ðŸ˜"
                
                # Save entry
                st.session_state.journal_entries.insert(0, {
                    'date': datetime.now(),
                    'content': entry_text,
                    'sentiment': sentiment,
                    'score': sentiment_score,
                    'emoji': emoji
                })
                
                st.success(f"âœ… Entry saved! AI Analysis: {emoji} {sentiment} (Score: {sentiment_score:.2f})")
                st.balloons()
                
                # Clear input
                st.session_state.clear_input = True
                st.session_state.temp_journal_text = ""
                st.rerun()
            else:
                st.warning("âš ï¸ Please write something before saving!")
    
    with col_btn2:
        if st.button("ðŸ—‘ï¸ Clear", use_container_width=True):
            st.session_state.clear_input = True
            st.session_state.temp_journal_text = ""
            st.rerun()

with col2:
    st.subheader("ðŸ’¡ Journaling Tips")
    
    with st.expander("âœï¸ Be Honest", expanded=True):
        st.write("Write freely without judgment. This is your safe space.")
    
    with st.expander("ðŸ’­ Express Emotions"):
        st.write("Don't hold back. Let your feelings flow onto the page.")
    
    with st.expander("ðŸ” Reflect on Patterns"):
        st.write("Review past entries to identify triggers and growth.")
    
    with st.expander("ðŸ™ Practice Gratitude"):
        st.write("Include things you're grateful for each day.")
    
    if SENTIMENT_AVAILABLE:
        st.success("""
        **ðŸ¤– AI Analysis Active**
        
        Using VADER sentiment analysis for accurate insights.
        """)
    else:
        st.info("""
        **ðŸ¤– Simple Analysis Mode**
        
        Using keyword-based sentiment analysis.
        
        For advanced AI analysis, install:
        ```
        pip install vaderSentiment
        ```
        """)

st.divider()

# Display journal entries
st.subheader("ðŸ“š Your Journal Entries")

if st.session_state.journal_entries:
    for idx, entry in enumerate(st.session_state.journal_entries):
        with st.container():
            col_date, col_sentiment = st.columns([3, 1])
            
            with col_date:
                st.caption(f"ðŸ“… {entry['date'].strftime('%B %d, %Y at %I:%M %p')}")
            
            with col_sentiment:
                st.markdown(f"**{entry['emoji']} {entry['sentiment']}**")
            
            st.markdown(f"_{entry['content']}_")
            
            col_score, col_actions = st.columns([2, 1])
            
            with col_score:
                st.caption(f"Sentiment Score: {entry['score']:.2f}")
            
            with col_actions:
                if st.button("ðŸ—‘ï¸ Delete", key=f"del_{idx}"):
                    st.session_state.journal_entries.pop(idx)
                    st.rerun()
            
            st.divider()
else:
    st.info("""
    ðŸ“ **No journal entries yet**
    
    Start writing to track your thoughts and feelings. Your first entry is just a few words away!
    """)

st.divider()
st.caption("ðŸ’™ Journaling helps you understand yourself better. Keep writing!")
