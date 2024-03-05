import streamlit as st
from utils.logger import log_decorator


@log_decorator
def render():
    st.title("LinguAI")

    st.write("")

    st.subheader("Rewrite Content to Current Skill Level")

    st.write("")
    st.write("")

    original_content = st.text_area(
    "Original Content to Rewrite",
    placeholder="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    )

    st.write("")
    st.write("")

    skill_options = ['Level 1', 'Level 2', 'Level 3']

    current_skill = st.selectbox("Current Skill Level", skill_options)

    st.write("")
    st.write("")

    st.button("Rewrite Content")
