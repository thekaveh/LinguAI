import streamlit as st
from utils.logger import log_decorator

from services.user_service import UserService
from services.state_service import StateService
from services.notification_service import NotificationService


def _add_linguai_note():
    st.markdown("""
    LinguAI stands out in the realm of language education by offering personalized learning experiences tailored to 
    individuals who have mastered the basics and are eager to advance their skills further. 
    Recognizing the unique challenges and goals of each learner, LinguAI leverages cutting-edge AI technology 
    to create a bespoke curriculum that adapts to the specific needs and learning pace of its users. 
    
    This approach not only enhances comprehension but also ensures that learners remain engaged and motivated throughout 
    their language learning journey. 
    """)


@log_decorator
def render():
    state_service = StateService.instance()

    # st.image("./static/logo.png", width=100)
    st.subheader("Personalized language learning for intermediate learners")
    st.image("./static/different-languages.jpeg", width=704)
    st.write("")

    if state_service.username is None:
        # User is not authenticated; show login or registration option
        if state_service.just_logged_out:
            NotificationService.greet(
                "Hope to see you again soon back here at LinguAI!"
            )
            state_service.just_logged_out = False

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Our Features:")
            st.write(
                "- Dynamic content generation based on your interests and proficiency level."
            )
            st.write("- Rewrite existing content to match your skill level")
            st.write("- Progress tracking to monitor your improvement.")
            st.markdown("""
                        With LinguAI, students can look forward to a seamless transition from basic understanding 
                        to advanced proficiency, making it an invaluable tool for anyone serious about language mastery.
                        """)

        with col2:
            st.write("")
            _add_linguai_note()

    else:
        # User is authenticated; show the rest of the content
        user = UserService.get_user_by_username_sync(state_service.username)

        if user.preferred_name:
            logged_in_user_display_name = f"{user.preferred_name} {user.last_name}"
        else:
            logged_in_user_display_name = f"{user.first_name} {user.last_name}"

        st.write(
            f"#### :orange[Welcome back to LinguAI, {logged_in_user_display_name}!]"
        )

        if state_service.just_logged_in:
            NotificationService.greet(
                message=f"Welcome back to LinguAI, {logged_in_user_display_name}!"
            )
            state_service.just_logged_in = False

        _add_linguai_note()
        # Add the rest of your application's components here

    col1, col2 = st.columns([2, 1])

    with col1:
        if state_service.username is None:
            st.image("./static/language.jpg")
    with col2:
        if state_service.username is None:
            st.write(
                "_LinguAI provides customized language learning for learners who are looking to take the next step to improve their comprehension after learning the basics. Sign up today to continue your learning and try out our personalized features!_"
            )

    # st.markdown("---")

    styling = """
        <style>
            [data-testid="stForm"] {
                background: #E8DAB2;
                width: 100%;
            }
            [data-testid="stForm"] div div div {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
        </style>
    """
    st.write(styling, unsafe_allow_html=True)
