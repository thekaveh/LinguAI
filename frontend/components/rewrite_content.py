import asyncio
from concurrent.futures import ThreadPoolExecutor

import streamlit as st
from typing import List

from core.config import Config
from schema.language import Language
from utils.logger import log_decorator
from schema.user import User
from services.user_service import UserService
from schema.rewrite_content import ContentRewriteReq
from services.rewrite_content_service import RewriteContentService
from services.skill_level_service import SkillLevelService
from services.language_service import LanguageService

@log_decorator
def _fetch_user_by_username_sync(username):
    # Wrapper function to call the async function synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(UserService.get_user_by_username(username))
    loop.close()
    return result


@log_decorator
def _get_user():
    # TODO: Add in logged in user details here
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_fetch_user_by_username_sync, Config.DEFAULT_USER_NAME)
        return future.result()

@log_decorator
def _add_welcome(user):
    welcome = f"""
    ### Hi, {user.first_name} {user.middle_name or ""} {user.last_name}!

    To get started, simply paste the text you'd like to convert into the text area below. 
    LinguAI can convert it into content that matches your skill level and language selected.

    """
    st.markdown(welcome, unsafe_allow_html=True)
    
def _add_instruction(user):
    welcome_= f"""

    ##### Get Started:
    
    1. Select **Topics** of Interest
    2. Choose the **Content Type**
    3. Select **Language**
      
    
    """
    
    st.markdown(welcome_, unsafe_allow_html=True)
    st.markdown(f"""
                Once you made your selection,**Click to Get Your Content**.
                \n Ready to dive in? receive personalized content tailored to your interests and skill level. 
                Let's embark on today's learning journey together!. 
                               
                """)


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
                if latest_assessment is None or user_assessment.assessment_date > latest_assessment.assessment_date:
                    latest_assessment = user_assessment

        # Display the language and its skill level
        if latest_assessment:
            skill_level = latest_assessment.skill_level
            st.write(f"###### {language}: {skill_level}")



@log_decorator
def _build_content_rewrite_request(
    user: User, input_content: str, skill_level: str, language: str
) -> ContentRewriteReq:
    # Build the ContentRewriteReq object
    content_rewrite_req = ContentRewriteReq(
        user_id=user.user_id,
        input_content=input_content,
        skill_level=skill_level,
        language=language,
    )

    return content_rewrite_req

@log_decorator
def stream_content(content_rewrite_req):
    # Placeholder for accumulated content
    if "content_stream" not in st.session_state:
        st.session_state["content_stream"] = ""

    # Define callback functions
    def on_next(content_chunk):
        # Append new content chunk to the existing content
        st.session_state["content_stream"] += content_chunk

    def on_completed():
        # Handle completion (e.g., clear session state if needed)
        pass

    # Async call to generate content (simplified example, adjust as needed)
    asyncio.run(
        RewriteContentService.arewrite_content(
            request=content_rewrite_req, on_next_fn=on_next, on_completed_fn=on_completed
        )
    )

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
def _render_skill_levels(skill_levels):
    options = [""] + [skill_level.level for skill_level in skill_levels]
    selected_option_index = st.selectbox("##### Select Skill Level", range(len(options)), format_func=lambda x: options[x])
    
    if selected_option_index > 0:
        selected_skill_level = skill_levels[selected_option_index - 1]
    else:
        selected_skill_level = None
    return selected_skill_level


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
        selected_language = st.radio("##### Select Learning Language", user.learning_languages)
        #st.write(f"You selected: {selected_language}")
    else:
        st.write("No learning languages specified.")
    return _get_language_object(user, selected_language)


@log_decorator
def _fetch_languages_sync():
    # Wrapper function to call the async function synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(LanguageService.list())
    loop.close()
    return result

@log_decorator
def _fetch_languages():
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_fetch_languages_sync)
        return future.result()

@log_decorator
def _render_language_dropdown(languages):
    options = [""] + [language.language_name for language in languages]
    selected_option_index = st.selectbox("##### Select Language", range(len(options)), format_func=lambda x: options[x])
    
    if selected_option_index > 0:
        selected_language = languages[selected_option_index - 1]
    else:
        selected_language = None
    return selected_language


@log_decorator
def render():
    st.session_state["content_stream"] = ""
    st.title("LinguAI")

    st.write("")

    st.subheader("Rewrite Content to Current Skill Level")

    st.write("")
    
    user = _get_user()
    
    if user is None:
        st.write("No user found")
        return
    
    _add_welcome(user)

    col1, col2 = st.columns([3,1])
    with col1:
        original_content = st.text_area(
            "", height=400, placeholder="Enter your text here...", 
            key="original_content")
    with col2:
        _add_skill_level_by_language(user)
    
    st.write("")
    st.write("")
    
    #skill_options = ['Level 1', 'Level 2', 'Level 3']

    #current_skill = st.selectbox("Current Skill Level", skill_options)
    
    #selected_language, skill_level=_add_skill_level_by_language(user)
    #call backend service to prcess the content.
    
    skill_levels = _fetch_skill_levels()
    languages=_fetch_languages()



    

    st.write("")
    st.write("")    
    st.markdown("#### Explore Rewritting in different levels and language")
    
    st.write("")
    col3, col4 = st.columns(2)
    # Add the first item to the first column
    with col3:
        skill_level=_render_skill_levels(skill_levels)

    # Add the second item to the second column
    with col4:        
        selected_language=_render_language_dropdown(languages)
        #selected_language=_select_learning_language(user)
    
    
    st.write("")
    st.write("")

    if skill_level is None or selected_language is None or original_content == "":
        st.markdown(
            '<div style="padding: 10px; border: 1px solid red; border-radius: 5px;">'
            '<b></b> Please Enter content int text area above, select a language and skill level.</div>',
            unsafe_allow_html=True
        )
        st.session_state["content_stream"] = ""
    else:
        # st.button("Rewrite Content")
        if st.button("Rewrite Content"):
            st.session_state["content_stream"] = ""
            content_rewrite_req = _build_content_rewrite_request(user, original_content, skill_level.level, selected_language.language_name)
            
            stream_content(content_rewrite_req)

    # Placeholder for the response from LLM
    # st.write("#### Content")

    # content = st.session_state.get('content_stream', '')

    placeholder = st.empty()

    # Update content dynamically
    content = st.session_state.get("content_stream", "")

    placeholder.markdown(f"""{content}""", unsafe_allow_html=True)
