import asyncio
import streamlit as st
from typing import List

from core.config import Config
from utils.logger import log_decorator

from schema.language import Language
from schema.user import User, UserTopicBase
from schema.content_gen import ContentGenReq

from services.user_service import UserService
from services.topic_service import TopicService
from services.state_service import StateService
from services.content_service import ContentService
from services.content_gen_service import ContentGenService
from services.text_to_speech_service import TextToSpeechService


@log_decorator
def _render_content_types(content_types):
    options = [content_type.content_name for content_type in content_types]
    selected_option = st.radio(
        "##### Select Content Type",
        options,
        format_func=lambda x: x,
        horizontal=True,
        index=None,
    )
    global selected_content_type
    selected_content_type = next(
        (ct for ct in content_types if ct.content_name == selected_option), None
    )


@log_decorator
def _fetch_topic_combo_options():
    topics = asyncio.run(TopicService.list())
    return [topic.topic_name for topic in topics]


@log_decorator
def _get_user_topics(user: User) -> List[UserTopicBase]:
    if user.user_topics:
        return user.user_topics
    else:
        return []


@log_decorator
def _render_topic_combo_options(combo_options):
    st.write("##### Topic Options")
    selected_options = []

    # Determine the number of options per row
    options_per_row = 3  # Adjust this number based on your UI/UX needs

    # Calculate the number of rows needed
    num_rows = (len(combo_options) + options_per_row - 1) // options_per_row

    for row in range(num_rows):
        # For each row, create a new set of columns
        cols = st.columns(options_per_row)
        for i in range(options_per_row):
            # Calculate the actual index of the option in the flat list
            option_index = row * options_per_row + i
            if option_index < len(combo_options):  # Check to avoid index out of range
                option = combo_options[option_index]
                with cols[i]:
                    # Use value parameter to set default selection
                    selected = st.checkbox(
                        option,
                        value=False,  # default_selection,
                        key=f"topic_option_{option_index}",
                    )
                    if selected:
                        selected_options.append(option)
    return selected_options


@log_decorator
def _build_content_gen_request(
    user,
    selected_topic_options,
    selected_content_type,
    language,
    model_name: str,
    temperature: float,
    float,
    last_assessment=None,
) -> ContentGenReq:

    if not last_assessment:
        skill_level = "beginner"
    else:
        skill_level = last_assessment.skill_level

    # Build the ContentGenReq object
    content_gen_req = ContentGenReq(
        user_id=user.user_id,
        user_topics=selected_topic_options,
        content=selected_content_type,
        language=language,
        skill_level=skill_level,
        model_name=model_name,
        temperature=temperature,
    )

    return content_gen_req


@log_decorator
def _add_welcome(user):
    # if user.preferred_name:
    #         user_first = user.preferred_name
    # else:
    #     user_first = user.first_name
    ### Hi, {user_first} {user.middle_name} {user.last_name}!
    welcome_ = f"""
    We're delighted to have you here. You're on the path to expanding your knowledge and skills. 
    Let's make today's learning session productive and engaging.
    """
    st.markdown(welcome_, unsafe_allow_html=True)


def _add_instruction(user):
    welcome_ = f"""

    ##### Get Started:
    
    1. Select **Topics** of Interest
    2. Choose the **Content Type**
    3. Select **Language**      
    
    """

    st.markdown(welcome_, unsafe_allow_html=True)
    st.markdown(
        f"""
                Once you made your selection, **Click to Get Your Content**.
                \n {user.first_name}, are you ready to dive in? receive personalized content tailored to your interests and skill level. 
                Let's embark on today's learning journey together!. 
                               
                """
    )


@log_decorator
def _add_skill_level_by_language(user):

    st.write("\n\n")
    st.write("##### Your Current Skills")

    if not user or not user.user_assessments or not user.learning_languages:
        st.write("No user or user assessments or learning languages found")
        return

    for language in user.learning_languages:
        latest_assessment = _get_last_assessment_by_language(user, language)

        if latest_assessment:
            skill_level = latest_assessment.skill_level
            st.write(f"###### {language} : {skill_level}")
        else:
            pass
            # st.write("No assessment found for this language")


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


def _get_language_object(user, language_name):
    language_object = None
    if user.user_assessments:
        for user_assessment in user.user_assessments:
            if user_assessment.language.language_name == language_name:
                language_object = user_assessment.language
                break
    return language_object


def _select_learning_language(user):

    if user.learning_languages:
        selected_language = st.radio(
            "##### Select Learning Language", user.learning_languages, index=None
        )
        # st.write(f"You selected: {selected_language}")
    else:
        st.write("No learning languages specified.")
    return _get_language_object(user, selected_language)


@log_decorator
def render():
    state_service = StateService.instance()

    model_name = state_service.model
    username = state_service.username
    temperature = state_service.temperature

    st.title("Content For You")

    user = UserService.get_user_by_username_sync(username)

    if user is None:
        st.write("No user found")
        return

    _add_welcome(user)
    st.markdown("---")

    user_topics = _get_user_topics(user)
    if user_topics:
        topic_combo_options = [topic.topic_name for topic in user_topics]
    else:
        # Fetch default topic combo options if the user has no topics
        topic_combo_options = _fetch_topic_combo_options()

    # Content type selection section
    content_types = asyncio.run(ContentService.list())

    col3, col4 = st.columns([1, 2])

    # Add _add_instruction(user) to column 1
    with col3:
        _add_instruction(user)

    # Add selected_topic_options and render_content_types to column 2
    with col4:
        selected_topic_options = _render_topic_combo_options(topic_combo_options)
        _render_content_types(content_types)
        selected_language = _select_learning_language(user)

    st.markdown("---")

    col_btn_gen, col_btn_clear, col_tts = st.columns([3, 2, 3])
    content_gen_placeholder = st.empty()

    state_service.content_reading = ""

    with col_tts:
        audio_placeholder = st.empty()
    with col_btn_gen:
        if st.button("Click to Get Your Content", type="primary"):
            error = []
            if not selected_topic_options:
                error.append("You have to Select at least one topic.")
            if not selected_content_type:
                error.append("You have to Select at least one content type.")
            if not selected_language:
                error.append("You have to Select at least one language.")
            if error:
                st.markdown("##### Please correct the following errors:")
                for err in error:
                    st.error(err)
                return

            last_assessment = _get_last_assessment_by_language(user, selected_language)
            state_service.content_reading = ""
            content_gen_req = _build_content_gen_request(
                user,
                selected_topic_options,
                selected_content_type,
                selected_language,
                model_name,
                temperature,
                last_assessment,
            )

            async def _content_on_changed(content):
                content_gen_placeholder.markdown(
                    f"""{content}""", unsafe_allow_html=True
                )

            async def _content_on_completed(content):
                state_service.content_reading = content

                audio_data = await TextToSpeechService.agenerate(
                    lang="en",
                    text=content,
                )

                audio_html = f'<audio src="{audio_data.audio}" controls="controls" autoplay="autoplay" type="audio/mpeg"/>'
                audio_placeholder.markdown(audio_html, unsafe_allow_html=True)

            asyncio.run(
                ContentGenService.agenerate_content(
                    request=content_gen_req,
                    on_changed_fn=_content_on_changed,
                    on_completed_fn=_content_on_completed,
                )
            )
    with col_btn_clear:
        if st.button("Clear", type="primary"):
            state_service.content_reading = ""
            st.rerun()
