import streamlit as st
from utils.logger import log_decorator
import asyncio
from services.user_service import UserService
from services.state_service import StateService
from services.topic_service import TopicService
from services.language_service import LanguageService
from services.state_service import StateService


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

    st.subheader("General Information")
    st.write(f"Username: {user.username}")
    st.write(f"First Name: {user.first_name}")
    st.write(f"Last Name: {user.last_name}")
    st.write(f"Base Language: {user.base_language}")
    st.write(f"Learning Languages: {', '.join(user.learning_languages)}")

    st.subheader("Contact Information")
    st.write(f"Email: {user.email}")
    st.write(f"Registered Phone: {user.mobile_phone}")
    st.write(f"Contact Preference: {user.contact_preference}")

    # st.subheader("Additional Information")
    # st.write(f"User Topics: {user.user_topics}")
    # st.write(f"User Assessments: {user.user_assessments}")

    # st.image("./static/profile.png", width=225)

    # st.write("")

    # st.write("Name: ")

    # st.write("Username: ")

    # st.write("Comprehension Level: ")

    # st.write("Other Information...")

    # st.write("")

    # st.button("Change Password")
