import streamlit as st
from utils.logger import log_decorator
from streamlit_modal import Modal

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
    """
    Renders the home page of the LinguAI application.

    If the user is not authenticated, it shows login or registration options along with the features of LinguAI.
    If the user is authenticated, it displays a welcome message and additional content based on the user's type.
    The function also handles the UI tour feature for non-admin users.

    Returns:
        None
    """
    state_service = StateService.instance()

    # st.image("./static/logo.png", width=100)
    st.subheader("Personalized language learning for intermediate learners")
    st.image("./static/different-languages.jpeg", use_column_width="auto")
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
            NotificationService.celebrate(
                message=f"Welcome back to LinguAI, **{logged_in_user_display_name}**!"
            )
            state_service.just_logged_in = False

        _add_linguai_note()

        if user.user_type != 'admin':
            # Tour Feature
            if state_service.tour_mode is None:
                start_ui_tour = st.button(label="Take UI Tour", type="primary")

                if start_ui_tour:
                    modal = Modal(
                        "LinguAI Tour",
                        key="tour-modal",
                        # Optional
                        padding=20,  # default value
                        max_width=500,  # default value
                    )

                    state_service.tour_mode = modal
                    state_service.last_visited = None
            else:
                resume_tour = st.button(label="Resume Tour")

                if resume_tour:
                    state_service.last_visited = -1

            if state_service.tour_mode is not None:
                state_service.last_visited = 0
                with state_service.tour_mode.container():
                    st.markdown("Hello! Welcome to the LinguAI tour!")
                    st.markdown(
                        "This is our home page where you can read about LinguAI and start your language learning journey."
                    )

                    st.markdown("Let's get started on the tour!")
                    st.write("")

                    col1, col2 = st.columns([1, 1], gap="large")

                    with col1:
                        st.button(f"Next Stop: Chat", key="switch_button", type="primary", use_container_width=True)

                    with col2:
                        exit_tour = st.button(f"Exit Tour", use_container_width=True)
                    
                    if exit_tour:
                        state_service.tour_mode = None
                        state_service.last_visited = -1
                        st.rerun()

                    st.markdown("""
                        <span style="font-size: x-small; font-style: italic;">Note: please use the "exit tour" button instead of the 'X' to exit out of the tour!</span>
                        """,
                        unsafe_allow_html=True
                    )

    col1, col2 = st.columns([2, 1])

    with col1:
        if state_service.username is None:
            st.image("./static/language.jpg", use_column_width="auto")
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
