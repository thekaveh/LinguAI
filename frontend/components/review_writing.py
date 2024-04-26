import asyncio
import datetime
import traceback

import streamlit as st
from typing import Optional
from langdetect import detect
# from concurrent.futures import ThreadPoolExecutor

from utils.logger import log_decorator

from schema.user import User
from schema.review_writing import ReviewWritingReq
from schema.user_assessment import UserAssessmentBase

from services.llm_service import LLMService
from services.user_service import UserService
from services.state_service import StateService
from services.skill_level_service import SkillLevelService
from services.text_to_speech_service import TextToSpeechService
from services.review_writing_service import ReviewWritingService
from schema.user_content import UserContentBase, UserContentSearch
from services.user_content_service import UserContentService


CONTENT_TYPE = 2  # trail purpose, need to move to enums

# Helper functions for review writing page

@log_decorator
def _add_welcome(user):
    # if user.preferred_name:
    #         user_first = user.preferred_name
    # else:
    #     user_first = user.first_name
    #    ### Hi, {user_first} {user.middle_name or ""} {user.last_name}!
    welcome = f"""
    To get started, Write the content that you want feedback in the text area below. 
    LinguAI can provide feedback on your written content based on your skill level, 
    and recommend how it can be further improved to get you to the next level.
    """
    st.markdown(welcome, unsafe_allow_html=True)


@log_decorator
def _add_skill_level_by_language(user):
    st.write("")
    st.write("")
    st.write("")
    st.write("##### Your Skill Level")
    st.write("---")
    if not user or not user.user_assessments or not user.learning_languages:
        st.write("No user or user assessments or learning languages found")
        return

    # Loop through each language in the user's learning languages
    for language in user.learning_languages:
        # Find the latest assessment for the current language
        latest_assessment = None
        for user_assessment in user.user_assessments:
            if user_assessment.language.language_name == language:
                if (
                    latest_assessment is None
                    or user_assessment.assessment_date
                    > latest_assessment.assessment_date
                ):
                    latest_assessment = user_assessment

        # Display the language and its skill level
        if latest_assessment:
            skill_level = latest_assessment.skill_level
            st.write(f"###### {language}: {skill_level}")


@log_decorator
def _get_next_skill_level(curr_skill_level: str) -> Optional[str]:
    skill_levels = asyncio.run(SkillLevelService.list())

    if skill_levels is None:
        return None

    # Convert skill levels to a dictionary for easier lookup
    skill_levels_dict = {level_obj.id: level_obj.level for level_obj in skill_levels}

    # Find the id for the given level
    given_level_id = None
    for level_obj in skill_levels:
        if level_obj.level == curr_skill_level:
            given_level_id = level_obj.id
            break

    # If the given level is not found, return None
    if given_level_id is None:
        return None

    # Find the next level based on the given level id
    next_level_id = given_level_id + 1
    if next_level_id not in skill_levels_dict:
        # If the next level id is not found, return the same level as a string
        return curr_skill_level

    # Return the next level as a string
    return skill_levels_dict[next_level_id]


@log_decorator
def _build_review_writing_request(
    user: User,
    input_content: str,
    curr_skill_level: str,
    next_skill_level: str,
    language: str,
    llm_id: int,
    temperature: float,
    strength: Optional[str] = None,
    weakness: Optional[str] = None,
) -> ReviewWritingReq:
    # Handle the case where strength or weakness might be None
    if strength is None:
        strength = ""  # Assign an empty string if strength is None
    if weakness is None:
        weakness = ""  # Assign an empty string if weakness is None

    # Build the ContentRewriteReq object
    review_writing_req = ReviewWritingReq(
        user_id=user.user_id,
        input_content=input_content,
        curr_skill_level=curr_skill_level,
        next_skill_level=next_skill_level,
        strength=strength,
        weakness=weakness,
        language=language,
        llm_id=llm_id,
        temperature=temperature,
    )

    return review_writing_req


def language_code_to_name(code):
    if code == "en":
        return "English"
    elif code == "de":
        return "German"
    elif code == "es":
        return "Spanish"
    elif code == "zh":
        return "Mandarin"
    elif code == "fr":
        return "French"
    else:
        return "unknown"


def _find_last_user_assessment(
    user: User, language: str
) -> Optional[UserAssessmentBase]:
    user_assessments = user.user_assessments

    if user_assessments is None:
        return None

    # Filter user assessments for the given language
    language_user_assessments = [
        ua for ua in user_assessments if ua.language.language_name == language
    ]

    # If no assessments found for the language, return None
    if not language_user_assessments:
        return None

    # Sort the assessments by assessment_date in descending order
    sorted_assessments = sorted(
        language_user_assessments, key=lambda x: x.assessment_date, reverse=True
    )

    # Return the first assessment (which is the latest one)
    return sorted_assessments[0]


@log_decorator
def render():
    """
    Renders the review writing content page and provides feedback on user's writing.

    This function is responsible for rendering the review writing content page and providing feedback on the user's writing based on their skill level and the language of their text.

    Returns:
        None
    """
    state_service = StateService.instance()

    if state_service.tour_mode != None:
        state_service.last_visited = 4
        with state_service.tour_mode.container():
            st.markdown('This is our review writing content page!')
            st.markdown("On this page, you can get personal feedback on content that you've written yourself based on your skill level and in the language of your text.\n")

            st.markdown('Let\'s continue with the tour!')
            st.write("")

            col1, col2 = st.columns([1, 1], gap="large")

            with col1:
                st.button(f"Next Stop: Translation Quiz", key='switch_button', type="primary", use_container_width=True)
            with col2:
                exit_tour = st.button("Exit Tour", use_container_width=True)
            
            if exit_tour:
                state_service.tour_mode = None
            
            st.markdown("""
                <span style="font-size: x-small; font-style: italic;">Note: please use the "exit tour" button instead of the 'X' to exit out of the tour!</span>
                """,
                unsafe_allow_html=True
            )

    state_service.review_writing = ""

    llm_id = state_service.content_llm.id
    temperature = state_service.content_temperature

    # st.subheader("Review your writing and get feedback on how to improve it.")
    st.write("")

    username = state_service.username
    user = UserService.get_user_by_username_sync(username)

    if user is None:
        st.write("No user found")
        return

    _render_sidebar_settings()
    _add_welcome(user)

    user_writing_content = st.text_area(
        "",
        height=400,
        placeholder="Enter your text here...",
        key="user_writing_content",
        value="",
    )
    announcement_placeholder = st.empty()
    col1, col2 = st.columns(2)
    with col2:
        button_placeholder = st.empty()
    with col1:
        audio_placeholder = st.empty()

    st.write("")

    # st.write("---")

    st.write("---")
    content_placeholder = st.empty()

    # Display initial or existing content if available
    if state_service.review_writing:
        content_placeholder.markdown(
            f"""{state_service.review_writing}""", unsafe_allow_html=True
        )

    _render_previous_delivered_contents(user)
    if user_writing_content is None or user_writing_content.strip() == "":
        return

    try:
        detected_language = detect(user_writing_content)

        if detected_language is "unknown":
            announcement_placeholder.markdown(
                f"""Hello {user.last_name}, {user.first_name}. The Language you provided is not supported by LinguAI. 
                 Please provide content in a supported language."""
            )
            return

        if detected_language is None:
            return

        user_entered_language = language_code_to_name(detected_language)
        announcement_placeholder.markdown(
            f"Text is written in : {user_entered_language}"
        )
        last_assessment = _find_last_user_assessment(user, user_entered_language)

        if last_assessment is None:
            curr_skill_level = "Beginner"
            next_skill_level = "Beginner"
            announcement_placeholder.markdown(
                f"""Hello {user.last_name}, {user.first_name}. We do not have any assessment for you in {user_entered_language}.
                     We recommend you to take an assessment first before we can provide feedback."""
            )
        else:
            curr_skill_level = last_assessment.skill_level
            next_skill_level = _get_next_skill_level(curr_skill_level)
            if next_skill_level is None:
                next_skill_level = curr_skill_level
            strength = ""
            if last_assessment.strength:
                strength = last_assessment.strength
            weakness = ""
            if last_assessment.weakness:
                weakness = last_assessment.weakness

        with button_placeholder.container():
            cant_review = (
                user_entered_language is None
                or curr_skill_level is None
                or next_skill_level is None
                or last_assessment is None
            )
            col3, col4 = st.columns([3, 1])
            with col4:
                if st.button("Clear", type="primary", use_container_width=True):
                    state_service.review_writing = ""
                    st.rerun()
            with col3:
                if st.button(
                    "Review Writing",
                    use_container_width=True,
                    disabled=cant_review,
                    type="primary",
                ):
                    if cant_review:
                        return

                    st.write("")
                    st.write("")
                    announcement_placeholder.markdown(
                        "#### Let's get your writing feedback!"
                    )

                    st.write("")
                    st.write("")

                    review_writing_req = _build_review_writing_request(
                        user,
                        user_writing_content,
                        curr_skill_level,
                        next_skill_level,
                        user_entered_language,
                        llm_id,
                        temperature,
                        strength,
                        weakness,
                    )

                    async def _content_on_changed(content):
                        content_placeholder.markdown(
                            f"""{content}""", unsafe_allow_html=True
                        )

                    async def _content_on_completed(content):
                        state_service.review_writing = content

                        if state_service.content_tts:
                            audio_data = await TextToSpeechService.agenerate(
                                lang="en", text=content
                            )
                            audio_html = f'<audio src="{audio_data.audio}" controls="controls" autoplay="autoplay" type="audio/mpeg"/>'
                            audio_placeholder.markdown(
                                audio_html, unsafe_allow_html=True
                            )

                    asyncio.run(
                        ReviewWritingService.areview_writing(
                            review_writing_req,
                            on_changed_fn=_content_on_changed,
                            on_completed_fn=_content_on_completed,
                        )
                    )
                    if state_service.review_writing:
                        _save_content_for_later(
                            user,
                            user_writing_content,
                            state_service.review_writing,
                            curr_skill_level,
                            user_entered_language,
                        )

    except Exception:
        announcement_placeholder.write("Please input content in a supported language.")


# Additional helper functions

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
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("##### :orange[Your Content]")
                            st.text_area(
                                "User Content",
                                value=selected_content.user_content,
                                height=300,
                                disabled=True,
                            )
                        with col2:
                            st.markdown("##### :orange[Writing Feedback]")
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
            key="content_llm",
            disabled=not content_llms,
            label="Large Language Model:",
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
            label="Creativity:",
            key="content_temperature",
            value=state_service.content_temperature,
            help="Content Generation LLM Engine Temperature",
        )
        state_service.content_temperature = new_content_temperature

        new_content_tts = st.checkbox(
            key="content_tts",
            label="Voiceover",
            value=state_service.content_tts,
            help="Content Generation Text-to-Speech",
        )
        state_service.content_tts = new_content_tts
