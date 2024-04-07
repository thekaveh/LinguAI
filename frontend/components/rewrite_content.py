import asyncio
import datetime
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
from schema.user_content import UserContentBase, UserContentSearch
from services.user_content_service import UserContentService


CONTENT_TYPE=1 # trail purpose, need to move to enums

@log_decorator
def _add_welcome(user):
    # if user.preferred_name:
    #         user_first = user.preferred_name
    # else:
    #     user_first = user.first_name
#    ### Hi, {user_first} {user.middle_name or ""} {user.last_name}!    
    welcome = f"""
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

    original_rewrite_content = st.text_area(
        "",
        height=400,
        placeholder="Enter your text here...",
        key="original_rewrite_content",
        value="",
    )

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
                    if state_service.rewrite_content:
                        _save_content_for_later(user, original_rewrite_content, state_service.rewrite_content, skill_level.level, selected_language.language_name)
            with col3:
                if st.button("Clear", type="primary", use_container_width=True):
                    state_service.rewrite_content = ""
                    st.rerun()         

                        
    #st.write("---")       
    _render_previous_delivered_contents(user)

def _save_content_for_later(user, original_content, generated_content, level, language_name):
    CONTENT_TYPE=1 # trail purpose, need to move to enums
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
        expiry_date=expiry_date
    )

    try:
        user_content_saved = asyncio.run(UserContentService.create_user_content(user_content))
    except Exception as e:
        pass

def _render_previous_delivered_contents(user):
    with st.container():
        st.markdown(f"#### :orange[Stored Contents]")

        try:
            user_contents = asyncio.run(UserContentService.search_user_contents(UserContentSearch(user_id=user.user_id, content_type=1)))
            if not user_contents:
                st.write("No Stored Content")
                return

            with st.expander(f":orange[Previously Stored Contents]"):
                content_options = {
                    f"Skill Level: {content.level} - Language {content.language} - Date:{content.created_date.strftime('%Y-%m-%d %H:%M')} - ID:{content.id}": content.id
                    for content in user_contents
                }
                selected_option = st.selectbox("Select Content", list(content_options.keys()), index=0)

                if selected_option:
                    selected_content_id = content_options[selected_option]
                    selected_content = next((content for content in user_contents if content.id == selected_content_id), None)
                    
                    st.write("---")
                    if selected_content:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("##### :orange[Your Content]")
                            st.text_area("User Content", value=selected_content.user_content, height=300, disabled=True)
                        with col2:
                            st.markdown("##### :orange[App Created Content]")
                            st.text_area("Generated Content", value=selected_content.gen_content, height=300, disabled=True)

                        if st.button("Delete Content"):
                            try:
                                response = asyncio.run(UserContentService.delete_user_content(selected_content.id))
                                #st.write(response)
                                if response:
                                    user_contents = [content for content in user_contents if content.id != selected_content.id]  # Remove deleted content
                                    st.experimental_rerun()  # Rerun the app to refresh the content list
                            except Exception as e:
                                if not str(e).startswith("No object"):
                                    #raise e  # Re-raise exception if it's not the specific "no object" error
                                    pass
                                st.success("Content deleted or already doesn't exist.")
        except Exception as e:
            pass
