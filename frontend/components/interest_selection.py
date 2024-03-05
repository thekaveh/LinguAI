import streamlit as st
from utils.logger import log_decorator


@log_decorator
def render():
    st.title("LinguAI")

    st.write("")

    st.subheader("Interest Selection")

    options = st.multiselect(
    'Select your interests below',
    ['Basketball', 'Acting', 'Travelling', 'Video Games', 'Cooking', 'Camping', 'Soccer', 'Science', 'Art', 'Music'],
    ['Art', 'Science'])

