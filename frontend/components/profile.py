import streamlit as st
from utils.logger import log_decorator
import asyncio
from services.user_service import UserService
from services.state_service import StateService

@log_decorator
def render():
    st.title("Profile")
    
    state_service = StateService.instance()

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
