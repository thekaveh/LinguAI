import asyncio
import streamlit as st
from typing import List

from core.config import Config
from utils.logger import log_decorator

from schema.user import User
from schema.language import Language
from schema.rewrite_content import ContentRewriteReq

from services.user_service import UserService
from services.state_service import StateService
from services.language_service import LanguageService
from services.skill_level_service import SkillLevelService
from services.text_to_speech_service import TextToSpeechService
from services.rewrite_content_service import RewriteContentService


@log_decorator
def _add_welcome(user):
    welcome = f"""
    ### Hi, {user.first_name} {user.middle_name or ""} {user.last_name}!

    To get started, simply paste the text you'd like to convert into the text area below. 
    LinguAI can convert it into content that matches your skill level and language selected.

    """
    st.markdown(welcome, unsafe_allow_html=True)



@log_decorator
def _add_skill_level_by_language(user):

    st.write("")
    st.write("")
    st.write("##### Your Skill Level")
    st.write("---")
    if not user or not user.user_assessments or not user.learning_languages:
        st.write("No user or user assessments or learning languages found")
        return

    # Loop through each language in the user's learning languages
    for language in user.learning_languages:
        latest_assessment = _get_last_assessment_by_language(user, language)

        # Display the language and its skill level
        if latest_assessment:
            skill_level = latest_assessment.skill_level
            st.write(f"###### {language}: {skill_level}")

def _get_last_assessment_by_language(user, language):
    latest_assessment = None
    for user_assessment in user.user_assessments:
        if user_assessment.language.language_name == language:
            if (
                latest_assessment is None
                or user_assessment.assessment_date
                > latest_assessment.assessment_date
            ):
                latest_assessment = user_assessment
    return latest_assessment



@log_decorator
def _build_content_rewrite_request(
    user: User, input_content: str, skill_level: str, 
    language: str, user_skill_level:str, user_base_lang:str, model: str, temperature: float) -> ContentRewriteReq:
    # Build the ContentRewriteReq object
    content_rewrite_req = ContentRewriteReq(
        user_id=user.user_id,
        input_content=input_content,
        skill_level=skill_level,
        language=language,
        model=model,
        temperature=temperature,
        user_skill_level=user_skill_level,
        user_base_language=user_base_lang
    )

    return content_rewrite_req


@log_decorator
def _render_skill_levels(skill_levels):
    options = [""] + [skill_level.level for skill_level in skill_levels]
    selected_option_index = st.selectbox(
        "##### Select Skill Level",
        range(len(options)),
        format_func=lambda x: options[x],
    )

    if selected_option_index > 0:
        selected_skill_level = skill_levels[selected_option_index - 1]
    else:
        selected_skill_level = None
    return selected_skill_level


@log_decorator
def _render_language_dropdown(languages):
    options = [""] + [language.language_name for language in languages]
    selected_option_index = st.selectbox(
        "##### Select Language", range(len(options)), format_func=lambda x: options[x]
    )

    if selected_option_index > 0:
        selected_language = languages[selected_option_index - 1]
    else:
        selected_language = None
    return selected_language


@log_decorator
def render():
    state_service = StateService.instance()

    st.title("LinguAI")

    st.write("")

    st.subheader("Rewrite Content to Current Skill Level")

    st.write("")

    username = state_service.username
    user = UserService.get_user_by_username_sync(username)

    if user is None:
        st.write("No user found")
        return

    _add_welcome(user)
    
    state_service.rewrite_content = ""
    
    col1, col2 = st.columns([3, 1])
    with col1:
        original_rewrite_content = st.text_area(
            "",
            height=400,
            placeholder="Enter your text here...",
            key="original_rewrite_content",
            value="",
        )
    with col2:
        _add_skill_level_by_language(user)

    st.write("")
    st.write("")

    skill_levels = asyncio.run(SkillLevelService.list())

    languages = asyncio.run(LanguageService.list())

    st.write("")
    st.write("")
    st.markdown("#### Explore Rewritting in different levels and language")

    st.write("")
    col3, col4 = st.columns(2)
    # Add the first item to the first column
    with col3:
        skill_level = _render_skill_levels(skill_levels)

    # Add the second item to the second column
    with col4:
        selected_language = _render_language_dropdown(languages)
        # selected_language=_select_learning_language(user)

    st.write("")
    st.write("")

    # Placeholders for different sections of the app
    button_placeholder = st.empty()
    st.write("---")
    content_placeholder = st.empty()
    #audio_placeholder = st.empty()

    # Display initial or existing rewritten content if available
    if state_service.rewrite_content:
        content_placeholder.markdown(
            f"""{state_service.rewrite_content}""", unsafe_allow_html=True
        )

    temperature = state_service.temperature
    model=state_service.model
    if user.base_language is None:
        user_base_lang = "english"
    else:
        user_base_lang = user.base_language


    with button_placeholder.container():
        if skill_level is None or selected_language is None or original_rewrite_content == "":
            st.markdown(
                '<div style="padding: 10px; border: 1px solid red; border-radius: 5px;">'
                "<b></b> Please Enter content int text area above, select a language and skill level.</div>",
                unsafe_allow_html=True,
            )
        else:
            col1, col2, col3 = st.columns([3,2,1])
            with col1:
                audio_placeholder = st.empty()
            with col2:
                if st.button("Rewrite Content", type="primary", use_container_width=True):
                    
                    user_skill_level=""
                    if selected_language:
                        last_assessment_info= _get_last_assessment_by_language(user, selected_language.language_name)
                        if last_assessment_info:
                            user_skill_level = last_assessment_info.skill_level

                    content_rewrite_req = _build_content_rewrite_request(
                        user,
                        original_rewrite_content,
                        skill_level.level,
                        selected_language.language_name,
                        user_skill_level,
                        user_base_lang,
                        model,
                        temperature
                    )

                    async def _content_on_changed(rewrite_content):
                        content_placeholder.markdown(
                            f"""{rewrite_content}""", unsafe_allow_html=True
                        )

                    async def _content_on_completed(rewrite_content):
                        state_service.rewrite_content = rewrite_content

                        audio_data = await TextToSpeechService.agenerate(
                            lang="en",
                            text=rewrite_content,
                        )

                        audio_html = f'<audio src="{audio_data.audio}" controls="controls" autoplay="autoplay" type="audio/mpeg"/>'
                        audio_placeholder.markdown(audio_html, unsafe_allow_html=True)

                    asyncio.run(
                        RewriteContentService.arewrite_content(
                            request=content_rewrite_req,
                            on_changed_fn=_content_on_changed,
                            on_completed_fn=_content_on_completed,
                        )
                    )
            with col3:
                if st.button("Clear", type="primary", use_container_width=True):
                    state_service.rewrite_content = ""
                    st.rerun()                

