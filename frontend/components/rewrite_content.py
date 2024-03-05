import asyncio
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
from typing import List

from core.config import Config
from schema.language import Language
from utils.logger import log_decorator
from schema.user import User, UserTopicBase
from schema.content_gen import ContentGenReq
from services.user_service import UserService
from services.topic_service import TopicService

from services.content_service import ContentService
from services.content_gen_service import ContentGenService
from schema.rewrite_content import ContentRewriteReq
from services.rewrite_content_service import RewriteContentService


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
    Our system will then convert it into content that matches your skill level.

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
    st.write("\n\n")
    st.write("##### Your Skill Level")
    
    if not user or not user.user_assessments or not user.learning_languages:
        st.write("No user or user assessments or learning languages found")
        return "", ""
    
    # Create a list of languages
    languages = user.learning_languages
    
    # Display a selectbox to choose a language
    selected_language = st.selectbox("**Select a Language**", languages)
    
    # Find the latest assessment for the selected language
    latest_assessment = None
    for user_assessment in user.user_assessments:
        if user_assessment.language.language_name == selected_language:
            if latest_assessment is None or user_assessment.assessment_date > latest_assessment.assessment_date:
                latest_assessment = user_assessment
    
    # Display the skill level for the selected language
    if latest_assessment:
        skill_level = latest_assessment.skill_level
        st.write(f"###### {selected_language} : {skill_level}")
    else:
        st.write(f"###### No assessment found for {selected_language}")
        
    return selected_language, skill_level

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
def stream_content(content_gen_req):
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
        RewriteContentService.rewrite_content(
            request=content_gen_req, on_next_fn=on_next, on_completed_fn=on_completed
        )
    )

@log_decorator
def render():
    st.title("LinguAI")

    st.write("")

    st.subheader("Rewrite Content to Current Skill Level")

    st.write("")
    
    user = _get_user()
    
    if user is None:
        st.write("No user found")
        return
    
    _add_welcome(user)

    original_content = st.text_area(
    "", placeholder="", )

    st.write("")
    st.write("")

    #skill_options = ['Level 1', 'Level 2', 'Level 3']

    #current_skill = st.selectbox("Current Skill Level", skill_options)
    
    selected_language, skill_level=_add_skill_level_by_language(user)
    #call backend service to prcess the content.
    
    
    

    st.write("")
    st.write("")

    #st.button("Rewrite Content")
    if st.button("Rewrite Content"):
        st.session_state["content_stream"] = ""
        content_rewrite_req=_build_content_rewrite_request(user, original_content,skill_level,selected_language)
        
        stream_content(content_rewrite_req)

    # Placeholder for the response from LLM
    # st.write("#### Content")

    # content = st.session_state.get('content_stream', '')

    placeholder = st.empty()

    # Update content dynamically
    content = st.session_state.get("content_stream", "")

    placeholder.markdown(f"""{content}""", unsafe_allow_html=True)
