import streamlit as st
from datetime import datetime
import time

st.set_page_config(page_title="AI Chat", page_icon="ðŸ’¬", layout="wide")

st.title("AI Mental Health Chat ðŸ’¬")
st.markdown("### Talk to your AI companion")

# Initialize chat history
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm your AI mental health companion. I'm here to listen and support you. How are you feeling today?",
            "timestamp": datetime.now()
        }
    ]

# Crisis alert
st.error("""
**âš ï¸ Important:** This AI chatbot is for support and information only. It's not a replacement for professional mental health care.

**In case of emergency (India):**
- **KIRAN**: 1800-599-0019 (24/7)
- **Vandrevala**: 1860-2662-345 (24/7)
- **Police**: 100 | **Ambulance**: 102
""")

st.divider()

# Chat container
chat_container = st.container()

with chat_container:
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            st.caption(message["timestamp"].strftime("%I:%M %p"))

# Quick responses
st.markdown("**Quick responses:**")
quick_responses = [
    "I'm feeling anxious",
    "I need someone to talk to",
    "I'm feeling stressed",
    "I'm having a good day",
    "I need coping strategies",
    "Tell me about mindfulness"
]

cols = st.columns(3)
for idx, response in enumerate(quick_responses):
    with cols[idx % 3]:
        if st.button(response, key=f"quick_{idx}", use_container_width=True):
            st.session_state.user_input = response
            st.rerun()

st.divider()

def get_bot_response(user_message):
    """Generate contextual bot responses"""
    message_lower = user_message.lower()
    
    # Crisis keywords
    if any(word in message_lower for word in ['suicide', 'kill myself', 'end my life', 'want to die']):
        return """I'm very concerned about what you're sharing. Please reach out to a crisis counselor immediately.

**ðŸš¨ Crisis Resources (India):**
- **KIRAN: 1800-599-0019** - Mental Health Helpline (24/7)
- **Vandrevala: 1860-2662-345** - Crisis Support (24/7)
- **Police: 100** | **Ambulance: 102** if you're in immediate danger

Your life matters, and help is available 24/7. Please reach out now."""
    
    # Anxiety
    elif any(word in message_lower for word in ['anxious', 'anxiety', 'worried', 'panic']):
        return """I hear that you're feeling anxious. That's a very common feeling, and it's okay to feel this way.

**Try this breathing exercise:**
1. Breathe in slowly for 4 counts
2. Hold for 4 counts
3. Exhale slowly for 4 counts
4. Repeat 3-5 times

Would you like to talk about what's making you feel anxious? Sometimes sharing helps."""
    
    # Stress
    elif any(word in message_lower for word in ['stress', 'stressed', 'overwhelmed']):
        return """Stress can feel overwhelming, but you're taking a positive step by acknowledging it.

**Quick stress relief tips:**
- Take short breaks throughout your day
- Practice deep breathing
- Break tasks into smaller steps
- Talk to someone you trust
- Go for a short walk

What's been causing you the most stress lately?"""
    
    # Depression
    elif any(word in message_lower for word in ['depressed', 'sad', 'hopeless', 'worthless']):
        return """I'm sorry you're feeling this way. Depression is a real condition, and you don't have to face it alone.

**Important:** Please consider talking to a mental health professional who can provide proper support.

**In the meantime:**
- Try to maintain a routine
- Get some sunlight if possible
- Reach out to loved ones
- Be gentle with yourself

Would you like some resources for professional help?"""
    
    # Good feelings
    elif any(word in message_lower for word in ['good', 'great', 'happy', 'better']):
        return """That's wonderful to hear! I'm so glad you're having a good day. ðŸ˜Š

What's been going well for you? Celebrating positive moments is important for mental health.

Keep up the great work!"""
    
    # Mindfulness
    elif any(word in message_lower for word in ['mindfulness', 'meditation', 'meditate']):
        return """Mindfulness is a powerful tool for mental health!

**Simple 5-minute exercise:**
1. Find a quiet spot
2. Close your eyes
3. Focus on your breathing
4. Notice the sensation of air entering and leaving
5. When your mind wanders, gently bring attention back to breath

Start with just 5 minutes a day. Would you like more mindfulness techniques?"""
    
    # Coping strategies
    elif any(word in message_lower for word in ['coping', 'strategies', 'help', 'techniques']):
        return """Here are some effective coping strategies:

1. **Deep breathing exercises** - Calms your nervous system
2. **Physical activity** - Even a short walk helps
3. **Journaling** - Write down your thoughts
4. **Talk to someone** - Share with a trusted person
5. **Engage in hobbies** - Do something you enjoy
6. **Progressive muscle relaxation** - Release physical tension

Which of these would you like to learn more about?"""
    
    # Sleep
    elif any(word in message_lower for word in ['sleep', 'insomnia', 'tired', 'exhausted']):
        return """Sleep is crucial for mental health. Here are some tips:

**Better sleep habits:**
- Stick to a consistent sleep schedule
- Avoid screens 1 hour before bed
- Keep your bedroom cool and dark
- Avoid caffeine after 2 PM
- Try relaxation techniques before bed

Are you having trouble falling asleep or staying asleep?"""
    
    # Default response
    else:
        return """Thank you for sharing that with me. I'm here to listen and support you.

Can you tell me more about how you're feeling? I'm here to help in any way I can.

**Remember:** If you're in crisis, please reach out to **KIRAN: 1800-599-0019** (India, free, 24/7) or your nearest emergency services."""

# Sidebar with resources
with st.sidebar:
    st.subheader("ðŸ†˜ Crisis Resources (India)")
    st.error("**1800-599-0019** - KIRAN Helpline")
    st.warning("**1860-2662-345** - Vandrevala Foundation")
    st.info("**100** - Police | **102** - Ambulance")
    
    st.divider()
    
    st.subheader("ðŸ’¡ Chat Tips")
    st.write("""
    - Be honest about your feelings
    - Take your time to express yourself
    - Ask for specific help if needed
    - Remember this is a support tool
    """)
    
    st.divider()

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Add user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Generate bot response
    bot_response = get_bot_response(user_input)
    
    # Add bot message
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": bot_response,
        "timestamp": datetime.now()
    })
    
    st.rerun()
    
    if st.button("ðŸ”„ New Conversation", use_container_width=True):
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your AI mental health companion. How can I support you today?",
                "timestamp": datetime.now()
            }
        ]
        st.rerun()

st.divider()
st.caption("ðŸ’™ This AI provides support but is not a replacement for professional mental health care.")
