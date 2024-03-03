
from typing import List
from services.content_gen_service import ContentGenService
import streamlit as st
import asyncio
from services.content_service import ContentService
from concurrent.futures import ThreadPoolExecutor
from models.schema.content import Content as ContentSchema
from services.topic_service import TopicService 
from services.user_service import UserService
from core.config import Config
from models.schema.user import User, UserTopicBase
from models.schema.language import Language
from models.schema.content_gen import ContentGenReq

def fetch_user_by_username_sync(username):
    # Wrapper function to call the async function synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(UserService.get_user_by_username(username))
    loop.close()
    return result

def get_user():
    # TODO: Add in logged in user details here
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fetch_user_by_username_sync, Config.DEFAULT_USER_NAME)
        return future.result()
    
    
def fetch_content_types_sync():
    # Wrapper function to call the async function synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(ContentService.list())
    loop.close()
    return result

def fetch_content_types():
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fetch_content_types_sync)
        return future.result()

def render_content_types(content_types):
    st.write("#### Select Content Type")
    options = [content_type.content_name for content_type in content_types]
    selected_option = st.radio("", options, format_func=lambda x: x, horizontal=True)
    global selected_content_type
    selected_content_type = next((ct for ct in content_types if ct.content_name == selected_option), None)
    

def fetch_topics_sync():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    topics = loop.run_until_complete(TopicService.list())
    loop.close()
    return topics

def fetch_topic_combo_options():
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fetch_topics_sync)
        topics = future.result()
    # Assuming topics is a list of Topic objects, extract the topic_name for each
    return [topic.topic_name for topic in topics]

def get_user_topics(user: User) -> List[UserTopicBase]:
    if user.user_topics:
        return user.user_topics
    else:
        return []


def render_topic_combo_options(combo_options):
    st.write("#### Topic Options")
    selected_options = []
    
    # Determine the number of options per row
    options_per_row = 4  # Adjust this number based on your UI/UX needs
    
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
                    if st.checkbox(option, key=f"topic_option_{option_index}"):
                        selected_options.append(option)
    return selected_options


def get_language():
    # TODO: Add in logged in user language selection here
    return Language(language_id=3, language_name=Config.DEFAULT_LANGUAGE)
            
def build_content_gen_request(user, selected_topic_options, selected_content_type, language) -> ContentGenReq:
    # Extract user_topics as a list of strings from selected_topic_options
    #user_topics = [topic.topic_name for topic in selected_topic_options]
    
    # Build the ContentGenReq object
    content_gen_req = ContentGenReq(
        user_id=user.user_id,
        user_topics=selected_topic_options,
        content=selected_content_type,
        language=language
    )
    
    return content_gen_req


def stream_content(content_gen_req):
    # Placeholder for accumulated content
    if 'content_stream' not in st.session_state:
        st.session_state['content_stream'] = ""

    # Define callback functions
    def on_next(content_chunk):
        # Append new content chunk to the existing content
        st.session_state['content_stream'] += content_chunk


    def on_completed():
        # Handle completion (e.g., clear session state if needed)
        pass

    # Async call to generate content (simplified example, adjust as needed)
    asyncio.run(ContentGenService.generate_content(
        request=content_gen_req,
        on_next_fn=on_next,
        on_completed_fn=on_completed
    ))
    
    
def get_welcome_message(user):
    return f"""
    ## Welcome, {user.first_name} {user.middle_name} {user.last_name}!
    
    We're delighted to have you here. As a {Config.DEFAULT_SKILL_LEVEL} learner, you're on the path to expanding your knowledge and skills. 
    Let's make today's learning session productive and engaging.
    
    **Get Started:**
    
    1. **Select a Topic of Interest:** Pick and choose available topics.
    2. **Choose the Content Type:** Select the type of content.
    3. **Get Your Content:** **"Click to Get Your Content"** button.
    
    Ready to dive in? receive personalized content tailored to your interests and skill level.  Let's embark on today's learning journey together!
    """

        
def render():
    st.title("Content For You")

    user = get_user()
    if user is None:
        st.write("No user found")
        return

    # Displaying the welcome message
    st.markdown(get_welcome_message(user), unsafe_allow_html=True)
    

    user_topics = get_user_topics(user)
    if user_topics:
        topic_combo_options = [topic.topic_name for topic in user_topics]
    else:
        # Fetch default topic combo options if the user has no topics
        topic_combo_options = fetch_topic_combo_options()   
        
    selected_topic_options = render_topic_combo_options(topic_combo_options)

    # Content type selection section
    content_types = fetch_content_types()
    render_content_types(content_types)
    

    if st.button("Click to Get Your Content"):
        st.session_state['content_stream'] = ""
        content_gen_req = build_content_gen_request(user, selected_topic_options, selected_content_type, get_language())
        stream_content(content_gen_req)
    
    
    # Placeholder for the response from LLM
    #st.write("#### Content")
    
    #content = st.session_state.get('content_stream', '')

    placeholder = st.empty()

    # Update content dynamically
    content = st.session_state.get('content_stream', '')
    
    placeholder.markdown(f"""{content}""", unsafe_allow_html=True)

