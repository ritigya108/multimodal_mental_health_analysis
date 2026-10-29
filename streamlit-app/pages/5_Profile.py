import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Profile", page_icon="ðŸ‘¤", layout="wide")

st.title("My Profile ðŸ‘¤")

# Initialize profile data
if 'profile' not in st.session_state:
    st.session_state.profile = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1 (555) 123-4567',
        'age': 28,
        'emergency_contact': 'Jane Doe - +1 (555) 987-6543',
        'bio': 'Working on improving my mental health one day at a time.',
        'join_date': 'January 2024',
        'total_mood_logs': 45,
        'total_journal_entries': 23,
        'current_streak': 7,
        'longest_streak': 14
    }

col1, col2 = st.columns([1, 2])

with col1:
    # Profile card
    st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background-color: #f0f2f6; border-radius: 1rem;">
            <div style="width: 120px; height: 120px; background-color: #6366f1; border-radius: 50%; 
                        display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; 
                        font-size: 3rem; color: white;">
                {st.session_state.profile['name'][0]}
            </div>
            <h2>{st.session_state.profile['name']}</h2>
            <p style="color: #6b7280;">{st.session_state.profile['email']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Stats
    st.subheader("ðŸ“Š Your Stats")
    
    st.metric("Member Since", st.session_state.profile['join_date'])
    st.metric("Mood Logs", st.session_state.profile['total_mood_logs'])
    st.metric("Journal Entries", st.session_state.profile['total_journal_entries'])
    st.metric("Current Streak", f"{st.session_state.profile['current_streak']} days ðŸ”¥")
    st.metric("Longest Streak", f"{st.session_state.profile['longest_streak']} days ðŸ†")

with col2:
    # Personal Information
    st.subheader("Personal Information")
    
    with st.form("profile_form"):
        name = st.text_input("Name", value=st.session_state.profile['name'])
        email = st.text_input("Email", value=st.session_state.profile['email'])
        phone = st.text_input("Phone", value=st.session_state.profile['phone'])
        age = st.number_input("Age", value=st.session_state.profile['age'], min_value=13, max_value=120)
        emergency_contact = st.text_input("Emergency Contact", value=st.session_state.profile['emergency_contact'])
        bio = st.text_area("Bio", value=st.session_state.profile['bio'], height=100)
        
        col_save, col_cancel = st.columns(2)
        with col_save:
            submitted = st.form_submit_button("ðŸ’¾ Save Changes", type="primary", use_container_width=True)
        with col_cancel:
            cancel = st.form_submit_button("âŒ Cancel", use_container_width=True)
        
        if submitted:
            st.session_state.profile.update({
                'name': name,
                'email': email,
                'phone': phone,
                'age': age,
                'emergency_contact': emergency_contact,
                'bio': bio
            })
            st.success("âœ… Profile updated successfully!")
            st.balloons()
    
    st.divider()
    
    # Notification Settings
    st.subheader("ðŸ”” Notification Settings")
    
    email_notif = st.toggle("Email Notifications", value=True, help="Receive updates via email")
    daily_reminder = st.toggle("Daily Check-in Reminders", value=True, help="Get reminded to log your mood")
    weekly_reports = st.toggle("Weekly Progress Reports", value=False, help="Receive weekly summaries")
    crisis_alerts = st.toggle("Crisis Alerts", value=True, help="Immediate support when needed")
    
    if st.button("ðŸ’¾ Save Notification Settings", use_container_width=True):
        st.success("âœ… Notification settings saved!")
    
    st.divider()
    
    # Security
    st.subheader("ðŸ”’ Security")
    
    col_sec1, col_sec2 = st.columns(2)
    with col_sec1:
        if st.button("ðŸ”‘ Change Password", use_container_width=True):
            st.info("Password change feature coming soon!")
    with col_sec2:
        if st.button("ðŸ” Two-Factor Auth", use_container_width=True):
            st.info("2FA setup coming soon!")
    
    if st.button("ðŸ“¥ Download My Data", use_container_width=True):
        st.info("Data export feature coming soon!")
    
    st.divider()
    
    # Danger Zone
    st.error("âš ï¸ **Danger Zone**")
    st.caption("These actions are permanent and cannot be undone.")
    
    col_del1, col_del2 = st.columns(2)
    with col_del1:
        if st.button("ðŸ—‘ï¸ Delete All Entries", use_container_width=True):
            if st.checkbox("I understand this action is permanent"):
                st.warning("This would delete all your journal entries and mood logs.")
    with col_del2:
        if st.button("âŒ Delete Account", use_container_width=True):
            if st.checkbox("I want to delete my account", key="delete_account"):
                st.error("This would permanently delete your account and all data.")

st.divider()
st.caption("ðŸ’™ Your data is secure and private. We never share your information with third parties.")
