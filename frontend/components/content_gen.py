import asyncio
import streamlit as st
from typing import List

from core.config import Config
from schema.language import Language
from utils.logger import log_decorator
from schema.user import User, UserTopicBase
from schema.content_gen import ContentGenReq
from services.user_service import UserService
from services.topic_service import TopicService
from concurrent.futures import ThreadPoolExecutor
from services.content_service import ContentService
from services.content_gen_service import ContentGenService


@log_decorator
def fetch_user_by_username_sync(username):
    # Wrapper function to call the async function synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(UserService.get_user_by_username(username))
    loop.close()
    return result


@log_decorator
def get_user():
    # TODO: Add in logged in user details here
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fetch_user_by_username_sync, Config.DEFAULT_USER_NAME)
        return future.result()


@log_decorator
def fetch_content_types_sync():
    # Wrapper function to call the async function synchronously
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(ContentService.list())
    loop.close()
    return result


@log_decorator
def fetch_content_types():
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fetch_content_types_sync)
        return future.result()


@log_decorator
def render_content_types(content_types):
    options = [content_type.content_name for content_type in content_types]
    selected_option = st.radio(
        "##### Select Content Type", options, format_func=lambda x: x, horizontal=True
    )
    global selected_content_type
    selected_content_type = next(
        (ct for ct in content_types if ct.content_name == selected_option), None
    )


@log_decorator
def fetch_topics_sync():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    topics = loop.run_until_complete(TopicService.list())
    loop.close()
    return topics


@log_decorator
def fetch_topic_combo_options():
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fetch_topics_sync)
        topics = future.result()
    # Assuming topics is a list of Topic objects, extract the topic_name for each
    return [topic.topic_name for topic in topics]


@log_decorator
def get_user_topics(user: User) -> List[UserTopicBase]:
    if user.user_topics:
        return user.user_topics
    else:
        return []


@log_decorator
def render_topic_combo_options(combo_options):
    st.write("##### Topic Options")
    selected_options = []

    # Determine the number of options per row
    options_per_row = 3  # Adjust this number based on your UI/UX needs

    # Calculate the number of rows needed
    num_rows = (len(combo_options) + options_per_row - 1) // options_per_row

    default_selection = True  # Track default selection
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
                        value=default_selection,
                        key=f"topic_option_{option_index}",
                    )
                    if selected:
                        selected_options.append(option)
                    default_selection = (
                        False  # Set default selection to False after first checkbox
                    )
    return selected_options


@log_decorator
def get_language():
    # TODO: Add in logged in user language selection here
    return Language(language_id=3, language_name=Config.DEFAULT_LANGUAGE)


@log_decorator
def build_content_gen_request(
    user, selected_topic_options, selected_content_type, language
) -> ContentGenReq:
    # Extract user_topics as a list of strings from selected_topic_options
    # user_topics = [topic.topic_name for topic in selected_topic_options]

    # Build the ContentGenReq object
    content_gen_req = ContentGenReq(
        user_id=user.user_id,
        user_topics=selected_topic_options,
        content=selected_content_type,
        language=language,
    )

    return content_gen_req


@log_decorator
def _add_welcome(user):
    welcome_ = f"""
    ### Hi, {user.first_name} {user.middle_name} {user.last_name}!
    
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
                Once you made your selection,**Click to Get Your Content**.
                \n Ready to dive in? receive personalized content tailored to your interests and skill level. 
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
        # st.write(f"Language: {language}")

        latest_assessment = None
        for user_assessment in user.user_assessments:
            if user_assessment.language.language_name == language:
                if (
                    latest_assessment is None
                    or user_assessment.assessment_date
                    > latest_assessment.assessment_date
                ):
                    latest_assessment = user_assessment

        if latest_assessment:
            skill_level = latest_assessment.skill_level
            st.write(f"###### {language} : {skill_level}")
        else:
            None
            # st.write("No assessment found for this language")


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
            "##### Select Learning Language", user.learning_languages
        )
        # st.write(f"You selected: {selected_language}")
    else:
        st.write("No learning languages specified.")
    return _get_language_object(user, selected_language)


@log_decorator
def render():
    st.title("Content For You")

    user = get_user()
    if user is None:
        st.write("No user found")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        _add_welcome(user)

    with col2:
        _add_skill_level_by_language(user)

    st.markdown("---")

    user_topics = get_user_topics(user)
    if user_topics:
        topic_combo_options = [topic.topic_name for topic in user_topics]
    else:
        # Fetch default topic combo options if the user has no topics
        topic_combo_options = fetch_topic_combo_options()

    # selected_topic_options = render_topic_combo_options(topic_combo_options)

    # Content type selection section
    content_types = fetch_content_types()
    # render_content_types(content_types)

    col3, col4 = st.columns([1, 2])

    # Add _add_instruction(user) to column 1
    with col3:
        _add_instruction(user)

    # Add selected_topic_options and render_content_types to column 2
    with col4:
        selected_topic_options = render_topic_combo_options(topic_combo_options)
        render_content_types(content_types)
        selected_language = _select_learning_language(user)

    st.markdown("---")

    if "content_stream" not in st.session_state:
        st.session_state["content_stream"] = ""

    if st.session_state["content_stream"]:
        st.markdown(f"""{st.session_state["content_stream"]}""", unsafe_allow_html=True)

    if st.button("Click to Get Your Content"):
        st.session_state["content_stream"] = ""
        content_gen_req = build_content_gen_request(
            user, selected_topic_options, selected_content_type, get_language()
        )

        content_gen_placeholder = st.empty()

        # Define callback functions
        def _content_gen_on_next(content_chunk):
            content_gen_placeholder.markdown(
                f"""{content_chunk}""", unsafe_allow_html=True
            )

        def _content_gen_on_completed(content):
            st.session_state["content_stream"] = content

        asyncio.run(
            ContentGenService.agenerate_content(
                request=content_gen_req,
                on_next_fn=_content_gen_on_next,
                on_completed_fn=_content_gen_on_completed,
            )
        )
