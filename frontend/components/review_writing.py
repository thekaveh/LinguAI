import asyncio
import traceback
import streamlit as st
from typing import Optional
from langdetect import detect
from concurrent.futures import ThreadPoolExecutor

from utils.logger import log_decorator

from schema.user import User
from schema.review_writing import ReviewWritingReq
from schema.user_assessment import UserAssessmentBase

from services.user_service import UserService
from services.state_service import StateService
from services.skill_level_service import SkillLevelService
from services.text_to_speech_service import TextToSpeechService
from services.review_writing_service import ReviewWritingService


@log_decorator
def _add_welcome(user):
    welcome = f"""
    ### Hi, {user.first_name} {user.middle_name or ""} {user.last_name}!

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
def _fetch_skill_levels_sync():
    # Wrapper function to call the async function synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(SkillLevelService.list())
    loop.close()
    return result


@log_decorator
def _fetch_skill_levels():
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_fetch_skill_levels_sync)
        return future.result()


@log_decorator
def _get_next_skill_level(curr_skill_level: str) -> Optional[str]:
    skill_levels = _fetch_skill_levels()

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
    state_service = StateService.instance()

    st.title("LinguAI")

    st.write("")

    st.subheader("Review your writing and get feedback on how to improve it.")

    st.write("")

    username = state_service.username
    user = UserService.get_user_by_username_sync(username)

    if user is None:
        st.write("No user found")
        return

    _add_welcome(user)

    col1, col2 = st.columns([3, 1])
    with col1:
        original_content = st.text_area(
            "",
            height=400,
            placeholder="Enter your text here...",
            key="original_content",
        )
    with col2:
        _add_skill_level_by_language(user)

    st.write("")
    st.write("")

    # Placeholders for different sections of the page
    button_placeholder = st.empty()
    st.write("---")
    announcement_placeholder = st.empty()
    st.write("---")
    content_placeholder = st.empty()
    audio_placeholder = st.empty()

    # Display initial or existing content if available
    if state_service.review_writing:
        content_placeholder.markdown(
            f"""{state_service.review_writing}""", unsafe_allow_html=True
        )

    if original_content is None or original_content.strip() == "":
        return

    try:
        detected_language = detect(original_content)

        if detected_language is "unknown":
            announcement_placeholder.markdown(
                f"""Hello {user.last_name}, {user.first_name}. The Language you provided is not supported by LinguAI. 
                 Please provide content in a supported language."""
            )
            return

        if detected_language is None:
            return

        selected_language = language_code_to_name(detected_language)
        announcement_placeholder.markdown(f"Text is written in : {selected_language}")
        last_assessment = _find_last_user_assessment(user, selected_language)

        if last_assessment is None:
            curr_skill_level = "Beginner"
            next_skill_level = "Beginner"
            announcement_placeholder.markdown(
                f"""Hello {user.last_name}, {user.first_name}. We do not have any assessment for you in {selected_language}.
                     We recommend you to take an assessment first before we can provide feedback."""
            )
        else:
            curr_skill_level = last_assessment.skill_level
            next_skill_level = _get_next_skill_level(curr_skill_level)

        with button_placeholder.container():
            cant_review = (
                selected_language is None
                or curr_skill_level is None
                or next_skill_level is None
                or last_assessment is None
            )
            if st.button(
                "Review Writing", use_container_width=True, disabled=cant_review
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
                    original_content,
                    curr_skill_level,
                    next_skill_level,
                    selected_language,
                    last_assessment.strength,
                    last_assessment.weakness,
                )

                async def _content_on_changed(content):
                    content_placeholder.markdown(
                        f"""{content}""", unsafe_allow_html=True
                    )

                async def _content_on_completed(content):
                    state_service.review_writing = content

                    audio_data = await TextToSpeechService.agenerate(
                        lang="en", text=content
                    )

                    audio_html = f'<audio src="{audio_data.audio}" controls="controls" autoplay="autoplay" type="audio/mpeg"/>'
                    audio_placeholder.markdown(audio_html, unsafe_allow_html=True)

                asyncio.run(
                    ReviewWritingService.areview_writing(
                        review_writing_req,
                        on_changed_fn=_content_on_changed,
                        on_completed_fn=_content_on_completed,
                    )
                )
    except Exception:
        announcement_placeholder.write("Please input content in a supported language.")
