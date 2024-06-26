import streamlit as st
import time
from utils.logger import log_decorator
import asyncio
from services.user_service import UserService
from services.topic_service import TopicService

from services.state_service import StateService


@log_decorator
def render():
    """
    Renders the interest selection component.

    This function displays a title, a subheader, and a multiselect widget for selecting interests.
    It retrieves the list of available topics from the TopicService and the current user's topics from the UserService.
    The selected interests are updated in the UserService and the page is rerun to reflect the changes.

    Returns:
        None
    """
    st.title("LinguAI")

    st.write("")

    st.subheader("Interest Selection")

    state_service = StateService.instance()

    topics = asyncio.run(TopicService.list())
    topics = [topic.topic_name for topic in topics]
    user = asyncio.run(UserService.get_user_by_username(state_service.username))
    current_user_topics = [topic.topic_name for topic in user.user_topics]
    options = st.multiselect('Select your interests below', topics, current_user_topics)
    
    if (len(options) > 0 and len(current_user_topics) != len(options)):
        asyncio.run(UserService.update_topics(options, state_service.username))
        st.experimental_rerun()
