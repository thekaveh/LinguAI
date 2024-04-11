import asyncio
import datetime
import streamlit as st
from typing import List

from core.config import Config
from utils.logger import log_decorator

from schema.language import Language
from schema.user import User, UserTopicBase
from schema.content_gen import ContentGenReq

from services.llm_service import LLMService
from services.user_service import UserService
from services.topic_service import TopicService
from services.state_service import StateService
from services.content_service import ContentService
from services.content_gen_service import ContentGenService
from services.text_to_speech_service import TextToSpeechService
from schema.user_content import UserContentBase, UserContentSearch
from services.user_content_service import UserContentService


CONTENT_TYPE = (
    3  # move to enums later, tells this content is about the reading page content
)


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
    llm_id: int,
    temperature: float,
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
        llm_id=llm_id,
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

    llm_id = state_service.content_llm.id
    username = state_service.username
    temperature = state_service.content_temperature

    # st.subheader("Content For You")

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

    (
        col_tts,
        col_btn_gen,
        col_btn_clear,
    ) = st.columns([4, 3, 2])
    content_gen_placeholder = st.empty()

    state_service.content_reading = ""

    with col_tts:
        audio_placeholder = st.empty()
    with col_btn_gen:
        if st.button(
            "Click to Get Your Content", type="primary", use_container_width=True
        ):
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
                llm_id,
                temperature,
                last_assessment,
            )

            async def _content_on_changed(content):
                content_gen_placeholder.markdown(
                    f"""{content}""", unsafe_allow_html=True
                )

            async def _content_on_completed(content):
                state_service.content_reading = content

                if state_service.content_tts:
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
            if last_assessment:
                level = last_assessment.skill_level
            else:
                level = "beginner"
            if selected_language:
                content_lang = selected_language.language_name
            else:
                content_lang = "English"
            if state_service.content_reading:
                _save_content_for_later(
                    user, "", state_service.content_reading, level, content_lang
                )

    with col_btn_clear:
        if st.button("Clear", type="primary", use_container_width=True):
            state_service.content_reading = ""
            st.rerun()
    st.markdown("---")
    _render_previous_delivered_contents(user)

    _render_sidebar_settings()


def _save_content_for_later(
    user, original_content, generated_content, level, language_name
):
    # Calculate the current time (created_date) and 7 days from now (expiry_date)
    created_date = datetime.datetime.now(datetime.timezone.utc)
    expiry_date = created_date + datetime.timedelta(days=7)

    # Create the UserContentBase object with the calculated dates
    user_content = UserContentBase(
        user_id=user.user_id,
        user_content=original_content,
        gen_content=generated_content,
        type=CONTENT_TYPE,
        level=level,
        language=language_name,
        created_date=created_date,
        expiry_date=expiry_date,
    )

    try:
        user_content_saved = asyncio.run(
            UserContentService.create_user_content(user_content)
        )
    except Exception as e:
        pass


def _render_previous_delivered_contents(user):
    with st.container():
        st.markdown(f"#### :orange[History]")

        try:
            user_contents = asyncio.run(
                UserContentService.search_user_contents(
                    UserContentSearch(user_id=user.user_id, content_type=CONTENT_TYPE)
                )
            )
            if not user_contents:
                st.write("No History Found.")
                return

            with st.expander(f":orange[Previously Stored Contents]"):
                content_options = {
                    f"Skill Level: {content.level} - Language {content.language} - Date:{content.created_date.strftime('%Y-%m-%d %H:%M')} - ID:{content.id}": content.id
                    for content in user_contents
                }
                selected_option = st.selectbox(
                    "Select Content", list(content_options.keys()), index=0
                )

                if selected_option:
                    selected_content_id = content_options[selected_option]
                    selected_content = next(
                        (
                            content
                            for content in user_contents
                            if content.id == selected_content_id
                        ),
                        None,
                    )

                    st.write("---")
                    if selected_content:
                        st.markdown("##### :orange[App Created Content]")
                        st.text_area(
                            "Generated Content",
                            value=selected_content.gen_content,
                            height=300,
                            disabled=True,
                        )
                        if st.button("Delete Content"):
                            try:
                                response = asyncio.run(
                                    UserContentService.delete_user_content(
                                        selected_content.id
                                    )
                                )
                                # st.write(response)
                                if response:
                                    user_contents = [
                                        content
                                        for content in user_contents
                                        if content.id != selected_content.id
                                    ]  # Remove deleted content
                                    st.experimental_rerun()  # Rerun the app to refresh the content list
                            except Exception as e:
                                if not str(e).startswith("No object"):
                                    # raise e  # Re-raise exception if it's not the specific "no object" error
                                    pass
                                st.success("Content deleted or already doesn't exist.")
        except Exception as e:
            pass


def _render_sidebar_settings():
    state_service = StateService.instance()

    st.sidebar.write("---")

    with st.sidebar.expander("⚙️", expanded=True):
        content_llms = LLMService.get_content()
        new_content_llm = st.selectbox(
            label="Content LLM:",
            key="content_llm",
            disabled=not content_llms,
            help="Content Generation LLM Engine",
            format_func=lambda llm: llm.display_name(),
            options=content_llms if content_llms else ["No LLMs available!"],
            index=0
            if not (content_llms or state_service.content_llm)
            else content_llms.index(
                next(
                    (
                        llm
                        for llm in content_llms
                        if llm.id == state_service.content_llm.id
                    ),
                    content_llms[0],
                )
            ),
        )
        state_service.content_llm = (
            new_content_llm if new_content_llm != "No LLMs available!" else None
        )

        new_content_temperature = st.slider(
            step=0.1,
            min_value=0.0,
            max_value=1.0,
            label="Content Temperature:",
            key="content_temperature",
            value=state_service.content_temperature,
            help="Content Generation LLM Engine Temperature",
        )
        state_service.content_temperature = new_content_temperature

        new_content_tts = st.checkbox(
            key="content_tts",
            label="Content TTS",
            value=state_service.content_tts,
            help="Content Generation Text-to-Speech",
        )
        state_service.content_tts = new_content_tts
