import asyncio
import streamlit as st

from services.state_service import StateService
from services.user_service import UserService


def _get_last_assessment_by_language(user, language):
    """
    Get the last assessment for a specific language for a given user.

    Args:
        user (User): The user for whom to retrieve the assessment.
        language (str): The name of the language for which to retrieve the assessment.

    Returns:
        Assessment or None: The last assessment for the specified language, or None if no assessment is found.
    """
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
    """
    Adds skill levels for each language the user is learning.

    Args:
        user (User): The user object containing user information.

    Returns:
        None
    """
    with st.expander(f":orange[Your Current Skill Levels]"):
        # Your original Markdown line needs to be converted as it won't render emojis correctly in HTML context
        #st.markdown("<h5 style='color: orange;'>Your Current Skills</h5>", unsafe_allow_html=True)
        if not user or not user.user_assessments or not user.learning_languages:
            st.write("No user or user assessments or learning languages found")
            return
        for language in user.learning_languages:
            latest_assessment = _get_last_assessment_by_language(user, language)
            if latest_assessment:
                skill_level = latest_assessment.skill_level
                st.write(f"###### :orange[{language}] : {skill_level}")

def _welcome(user):
    """
    Displays a welcome message to the user.

    Parameters:
        user (User): The user object containing user information.

    Returns:
        None
    """
    welcome_container = st.container()
    with welcome_container:
        col1, col2 = st.columns([3, 2])
        with col1:
            if user.preferred_name:
                st.markdown(f"### Hi, {user.preferred_name}")
            else:
                st.markdown(f"### Hi, {user.first_name} {user.last_name}")
        with col2:
             _add_skill_level_by_language(user)    
        st.write("---")

def render():
    """
    Renders the header component.

    This function displays the header component, which includes a logo image and a welcome message for the logged-in user.

    Parameters:
        None

    Returns:
        None
    """
    state_service = StateService.instance()
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("./static/logo5.png", width=150)
    with col2:
        if state_service.username is not None:
            user = asyncio.run(UserService.get_user_by_username(state_service.username))
            _welcome(user)
