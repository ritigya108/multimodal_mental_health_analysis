import streamlit as st

st.set_page_config(page_title="Resources", page_icon="ðŸ“š", layout="wide")

st.title("Mental Health Resources ðŸ“š")
st.markdown("### Curated resources to support your mental health journey")

# Emergency alert
st.error("""
**ðŸš¨ In Crisis? Get Help Now (India)**

If you're in immediate danger, call **100** (Police) or **102** (Ambulance).

For mental health crisis support:
- **KIRAN**: 1800-599-0019 (24/7)
- **Vandrevala Foundation**: 1860-2662-345 (24/7)
- **iCall**: 9152987821 (Mon-Sat, 8 AM - 10 PM)
""")

st.divider()

# Search
search = st.text_input("ðŸ” Search resources...", placeholder="Search for articles, videos, exercises...")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["ðŸ“ž Crisis Hotlines", "ðŸ“„ Articles", "ðŸŽ¥ Videos", "ðŸ§˜ Exercises"])

with tab1:
    st.subheader("Crisis Hotlines")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.error("""
        ### ðŸš¨ KIRAN Mental Health Helpline
        **24/7 free and confidential support**
        
        **Call: 1800-599-0019**
        
        Ministry of Social Justice & Empowerment initiative for mental health support.
        """)
        
        st.warning("""
        ### ðŸ’¬ Vandrevala Foundation
        **24/7 crisis support**
        
        **Call: 1860-2662-345**
        **Call: 1800-2333-330**
        
        Free counseling and crisis intervention services.
        """)
        
        st.info("""
        ### ðŸ¥ iCall Psychosocial Helpline
        **Professional counseling**
        
        **Call: 9152987821**
        
        Monday-Saturday, 8 AM - 10 PM
        Email: icall@tiss.edu
        """)
    
    with col2:
        st.info("""
        ### ðŸŽ—ï¸ NIMHANS Helpline (Bangalore)
        **Mental health support**
        
        **Call: 080-46110007**
        
        Monday-Saturday, 9 AM - 5:30 PM
        """)
        
        st.success("""
        ### ðŸ¤ Snehi (Delhi NCR)
        **Emotional support**
        
        **Call: 011-65978181**
        
        Monday-Saturday, 10 AM - 8 PM
        """)
        
        st.warning("""
        ### ðŸŒˆ Mitram Foundation (Chennai)
        **LGBTQ+ support**
        
        **Call: 044-24640050**
        
        Specialized support for LGBTQ+ community
        """)

with tab2:
    st.subheader("Educational Articles")
    
    articles = [
        {
            "title": "Understanding Depression: Signs and Symptoms",
            "desc": "Learn about the common signs of depression and when to seek help",
            "category": "Mental Health",
            "time": "8 min read",
            "url": "https://www.nimh.nih.gov/health/topics/depression"
        },
        {
            "title": "Anxiety Management Techniques",
            "desc": "Practical strategies to manage anxiety in daily life",
            "category": "Coping Skills",
            "time": "10 min read",
            "url": "https://www.nami.org/About-Mental-Illness/Mental-Health-Conditions/Anxiety-Disorders"
        },
        {
            "title": "The Importance of Sleep for Mental Health",
            "desc": "How sleep affects your mental well-being and tips for better sleep",
            "category": "Wellness",
            "time": "6 min read",
            "url": "https://www.sleepfoundation.org/mental-health"
        },
        {
            "title": "Building Resilience in Difficult Times",
            "desc": "Develop skills to bounce back from challenges",
            "category": "Personal Growth",
            "time": "12 min read",
            "url": "https://www.apa.org/topics/resilience"
        }
    ]
    
    for article in articles:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### ðŸ“„ {article['title']}")
                st.write(article['desc'])
                st.caption(f"ðŸ·ï¸ {article['category']} â€¢ â±ï¸ {article['time']}")
            with col2:
                st.link_button("Read Article", article['url'], use_container_width=True)
            st.divider()

with tab3:
    st.subheader("Video Resources")
    
    videos = [
        {
            "title": "Guided Meditation for Anxiety Relief",
            "desc": "10-minute guided meditation to calm your mind",
            "duration": "10:00",
            "category": "Meditation"
        },
        {
            "title": "Understanding Mental Health - TED Talk",
            "desc": "Breaking the stigma around mental health",
            "duration": "15:30",
            "category": "Education"
        },
        {
            "title": "Breathing Exercises for Stress",
            "desc": "Simple breathing techniques you can do anywhere",
            "duration": "5:45",
            "category": "Wellness"
        },
        {
            "title": "Yoga for Mental Health",
            "desc": "Gentle yoga practice for emotional well-being",
            "duration": "20:00",
            "category": "Exercise"
        }
    ]
    
    cols = st.columns(2)
    for idx, video in enumerate(videos):
        with cols[idx % 2]:
            st.info(f"""
            ### ðŸŽ¥ {video['title']}
            
            {video['desc']}
            
            **Duration:** {video['duration']} â€¢ **Category:** {video['category']}
            """)
            st.button("Watch Video", key=f"video_{idx}", use_container_width=True)

with tab4:
    st.subheader("Practical Exercises")
    
    exercises = [
        {
            "title": "Progressive Muscle Relaxation",
            "desc": "Systematically tense and relax muscle groups to reduce stress",
            "duration": "15 min",
            "difficulty": "Beginner"
        },
        {
            "title": "5-4-3-2-1 Grounding Technique",
            "desc": "Use your senses to ground yourself in the present moment",
            "duration": "5 min",
            "difficulty": "Beginner"
        },
        {
            "title": "Box Breathing",
            "desc": "Breathe in a pattern to calm your nervous system",
            "duration": "5 min",
            "difficulty": "Beginner"
        },
        {
            "title": "Body Scan Meditation",
            "desc": "Bring awareness to different parts of your body",
            "duration": "20 min",
            "difficulty": "Intermediate"
        },
        {
            "title": "Gratitude Journaling",
            "desc": "Write down things you're grateful for each day",
            "duration": "10 min",
            "difficulty": "Beginner"
        },
        {
            "title": "Mindful Walking",
            "desc": "Practice mindfulness while walking outdoors",
            "duration": "15 min",
            "difficulty": "Beginner"
        }
    ]
    
    cols = st.columns(3)
    for idx, exercise in enumerate(exercises):
        with cols[idx % 3]:
            difficulty_color = "ðŸŸ¢" if exercise['difficulty'] == "Beginner" else "ðŸŸ¡"
            st.success(f"""
            ### ðŸ§˜ {exercise['title']}
            
            {exercise['desc']}
            
            **â±ï¸ {exercise['duration']}** â€¢ **{difficulty_color} {exercise['difficulty']}**
            """)
            st.button("Try Exercise", key=f"ex_{idx}", use_container_width=True)

st.divider()

# Professional help
st.info("""
### ðŸ¥ Find Professional Help

These resources can help you find mental health professionals in your area:
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.link_button("Psychology Today", "https://www.psychologytoday.com/us/therapists", use_container_width=True)
with col2:
    st.link_button("NAMI Support", "https://www.nami.org/findsupport", use_container_width=True)
with col3:
    st.link_button("SAMHSA", "https://www.samhsa.gov/find-help/national-helpline", use_container_width=True)

st.divider()
st.caption("ðŸ’™ Remember: These resources complement but don't replace professional mental health care.")
