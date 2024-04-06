import streamlit as st
from utils.logger import log_decorator
import asyncio
from services.user_service import UserService
from services.state_service import StateService
from services.topic_service import TopicService
from services.language_service import LanguageService
from services.state_service import StateService
from concurrent.futures import ThreadPoolExecutor
from schema.user import UserCreate
from datetime import date, datetime


@log_decorator
def _fetch_languages_sync():
    # Wrapper function to call the async function synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(LanguageService.list())
    loop.close()
    return result

@log_decorator
def _fetch_languages():
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_fetch_languages_sync)
        return future.result()

@log_decorator
def _render_language_dropdown(languages, current_lang):
    options = [current_lang] + [language.language_name for language in languages]
    selected_option_index = st.selectbox("Select Base Language*", range(len(options)), format_func=lambda x: options[x])
    
    if selected_option_index > 0:
        selected_base_language = languages[selected_option_index - 1]
    else:
        selected_base_language = None
    if selected_base_language:
        return selected_base_language.language_name
    else:
        return ""
    
@log_decorator
def render_awards(user):
    today = date.today()
    awards = []

    # Check for the "Consistent Learner" award
    if user.consecutive_login_days and user.consecutive_login_days >= 30:
        awards.append("Consistent Learner 📅")


    # Check for the "New User" award
    if user.enrollment_date:
        days_since_enrollment = (today - user.enrollment_date).days
        if days_since_enrollment <= 10:
            awards.append("New User 🌟")


    # Check for the "Language Explorer" award
    if user.learning_languages and len(user.learning_languages) >= 3:
        awards.append("Language Explorer 🌍")


    # Check for the "Topic Master" award
    if user.enrollment_date:
        days_since_enrollment = (today - user.enrollment_date).days
        if days_since_enrollment >= 100:
            awards.append("Long Time User 🎓")


    # Display the awards
    if awards:
        for award in awards:
            st.markdown(f"* {award}")
    else:
        st.write("No awards yet. Keep engaging with the app to earn your first award!")
        
@log_decorator
def render_awards_info():
    with st.expander("Awards Information", expanded=False):
        st.subheader("Understand Your Awards")


        # Descriptions for each award
        awards_descriptions = {
            "Consistent Learner 📅": "Awarded for logging in and engaging with the app for 30 consecutive days.",
            "New User 🌟": "A warm welcome award for joining our community today! Let's embark on this learning journey together.",
            "Language Explorer 🌍": "Granted to language aficionados who are learning 3 or more languages. Keep exploring!",
            "Topic Master 🎓": "Earned by users who've been with us for over 100 days, showing dedication and mastery over their learning topics."
        }


        for award, description in awards_descriptions.items():
            st.markdown(f"**{award}**: {description}")

@log_decorator
def render():
    st.title("Profile")
    state_service = StateService.instance()
    user = asyncio.run(UserService.get_user_by_username(state_service.username))
    
    ### user awards (gamification)
    st.subheader("Your Awards 🏆")
    render_awards(user)
    st.write(f"* Daily Streak: {user.consecutive_login_days}")
    
    ### interest selection
    st.subheader("Interest Selection")


    topics = asyncio.run(TopicService.list())
    topics = [topic.topic_name for topic in topics]
    current_user_topics = [topic.topic_name for topic in user.user_topics]
    options = st.multiselect('Select your interests below', topics, current_user_topics)
    
    if (len(options) > 0 and len(current_user_topics) != len(options)):
        asyncio.run(UserService.update_topics(options, state_service.username))
        st.experimental_rerun()
        
    ### language selection 
    st.write("")

    st.subheader("Language Selection")

    languages = asyncio.run(LanguageService.list())
    languages = [language.language_name for language in languages]

    current_user_languages = [language for language in user.learning_languages]
    options = st.multiselect('Select your learning languages below', languages, current_user_languages)
    
    if (len(options) > 0 and len(current_user_languages) != len(options)):
        asyncio.run(UserService.update_languages(options, state_service.username))
        st.experimental_rerun()

    ### User Information 
    st.subheader("User Profile/Security")

    # view/update user information     
    with st.expander("Click to view/update your profile", expanded=False):
        with st.form("profile_info"):
            st.subheader("General Information")
            st.write(f"Username: {user.username}")
            updated_first_name = st.text_input("First Name", user.first_name)
            updated_middle_name = st.text_input("Middle Name", user.middle_name)
            updated_last_name = st.text_input("Last Name", user.last_name)
            updated_preferred_name = st.text_input("Preferred Name", user.preferred_name)
            updated_base_language = _render_language_dropdown(_fetch_languages(), user.base_language)
            updated_gender = st.selectbox("Gender*", options=[user.gender, "Male", "Female", "Nonbinary", "Prefer not to say"])            

            st.subheader("Contact Information")
            updated_email = st.text_input("Email", user.email)
            updated_phone = st.text_input("Registered Phone", user.mobile_phone)
            contact_preference_entry = st.selectbox("Contact Preference:", options=[user.contact_preference, "Email", "Mobile"])
            if (contact_preference_entry == "Mobile"):
                updated_contact_preference = "mobile_phone"
            else:
                updated_contact_preference = "email"
                    
            submit_button = st.form_submit_button("Update Profile")
            
            if submit_button:
                updated_user_data = UserCreate(
                    username=user.username, # username cannot be modified
                    email = updated_email,
                    user_type="external",
                    first_name = updated_first_name,
                    last_name = updated_last_name,
                    middle_name = updated_middle_name,
                    preferred_name = updated_preferred_name,
                    base_language = updated_base_language,
                    gender = updated_gender,
                    mobile_phone = updated_phone,
                    contact_preference = updated_contact_preference,
                    password_hash = "test", #hardcoded does not get updated here 
                )
                try:
                    asyncio.run(UserService.update_user_profile(user.username, updated_user_data))
                    st.success("Profile updated successfully.")
                except Exception as e:
                    st.error(f"Failed to updated profile: {e}")
                    
    with st.expander("Click to change your password", expanded=False):                
        with st.form("change_password"):
            st.subheader("Change Password")
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            
            submit_password_change = st.form_submit_button("Change Password")
            
            if submit_password_change:
                if new_password != confirm_new_password:
                    st.error("New passwords do not match")
                else:
                    try:
                        # Assuming UserService has a method to call the backend password change endpoint
                        asyncio.run(UserService.change_password(
                        user.username, current_password, new_password))
                        st.success("Password changed successfully")
                    except Exception as e:
                        if "400 Bad Request" in str(e):
                            st.error("Incorrect current password entered")
                        else: 
                            st.error(f"Failed to change password: {e}")
                            
    ### Extra Information 
    st.subheader("Extra Info")
    render_awards_info()

