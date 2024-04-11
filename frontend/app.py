import streamlit as st
from core.config import Config
from utils.logger_config import setup_global_logging
from services.user_service import UserService
from services.state_service import StateService
from components import (
    sidebar,
    home,
    chat,
    admin,
    content_gen,
    profile,
    rewrite_content,
    review_writing,
    foot_notes,
    header,
    register,
)
import asyncio

# Setup global logging with a specific logger name
setup_global_logging(
    logger_name=Config.FRONTEND_LOGGER_NAME,
    log_filename=Config.FRONTEND_LOG_FILE,
    log_level=Config.FRONTEND_LOG_LEVEL,
)


def _get_last_assessment_by_language(user, language):
    latest_assessment = None
    for user_assessment in user.user_assessments:
        if user_assessment.language.language_name == language:
            if (
                latest_assessment is None
                or user_assessment.assessment_date > latest_assessment.assessment_date
            ):
                latest_assessment = user_assessment
    return latest_assessment


def _add_skill_level_by_language(user):
    with st.expander(f":orange[Your Current Skill Levels]"):
        # Your original Markdown line needs to be converted as it won't render emojis correctly in HTML context
        # st.markdown("<h5 style='color: orange;'>Your Current Skills</h5>", unsafe_allow_html=True)
        if not user or not user.user_assessments or not user.learning_languages:
            st.write("No user or user assessments or learning languages found")
            return
        for language in user.learning_languages:
            latest_assessment = _get_last_assessment_by_language(user, language)
            if latest_assessment:
                skill_level = latest_assessment.skill_level
                st.write(f"###### :orange[{language}] : {skill_level}")


def _welcome(user):
    welcome_container = st.container()
    with welcome_container:
        col1, col2 = st.columns([2, 1])
        with col1:
            if user.preferred_name:
                st.markdown(f"### :orange[Hi, {user.preferred_name} {user.last_name}]")
            else:
                st.markdown(f"### :orange[Hi, {user.username}]")
        with col2:
            _add_skill_level_by_language(user)
    st.write("---")


def main():
    state_service = StateService.instance()
    header.render()
    components_info = {
        "Home": {"icon": "house", "page": home},
        "New User Registration": {"icon": "person-plus", "page": register},
    }

    if state_service.username is not None:
        user = asyncio.run(UserService.get_user_by_username(state_service.username))
        # _welcome(user)

        if user.user_type == "admin":
            components_info = {
                "Home": {"icon": "house", "page": home},
                "Rewrite Content": {"icon": "pen", "page": rewrite_content},
                "Review Writing": {"icon": "pencil-square", "page": review_writing},
                "Content Reading": {"icon": "body-text", "page": content_gen},
                "Chat": {"icon": "chat", "page": chat},
                "Profile": {"icon": "person-circle", "page": profile},
                "Admin": {"icon": "person-gear", "page": admin},
            }
        else:
            components_info = {
                "Home": {"icon": "house", "page": home},
                "Rewrite Content": {"icon": "pen", "page": rewrite_content},
                "Review Writing": {"icon": "pencil-square", "page": review_writing},
                "Content Reading": {"icon": "body-text", "page": content_gen},
                "Chat": {"icon": "chat", "page": chat},
                "Profile": {"icon": "person-circle", "page": profile},
            }

    selected_component_name, selected_component = sidebar.show(components_info)
    st.subheader(selected_component_name)
    # Assuming sidebar.show() updates `st.session_state.current_page` based on the selected page
    selected_component.render()

    # Conditionally render foot_notes based on the current page
    if selected_component != chat:
        foot_notes.render()


if __name__ == "__main__":
    main()
