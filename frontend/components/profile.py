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
def render():
    st.title("Profile")
    
    ### interest selection
    st.write("")

    st.subheader("Interest Selection")

    state_service = StateService.instance()

    topics = asyncio.run(TopicService.list())
    topics = [topic.topic_name for topic in topics]
    user = asyncio.run(UserService.get_user_by_username(state_service.username))
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

    user = asyncio.run(UserService.get_user_by_username(state_service.username))
    current_user_languages = [language for language in user.learning_languages]
    options = st.multiselect('Select your learning languages below', languages, current_user_languages)
    
    if (len(options) > 0 and len(current_user_languages) != len(options)):
        asyncio.run(UserService.update_languages(options, state_service.username))
        st.experimental_rerun()
        
    # get user to view/update their information     
    user = asyncio.run(UserService.get_user_by_username(state_service.username))
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
                password_hash = "test", #hardcoded for now
            )
            try:
                asyncio.run(UserService.update_user_profile(user.username, updated_user_data))
                st.success("Profile updated successfully.")
            except Exception as e:
                st.error(f"Failed to updated profile: {e}")