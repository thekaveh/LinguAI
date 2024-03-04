import streamlit as st
from utils.logger import log_decorator


@log_decorator
def render():
    st.title("Profile")

    st.image("./static/profile.png", width=225)

    st.write("")

    st.write("Name: ")

    st.write("Username: ")

    st.write("Comprehension Level: ")

    st.write("Other Information...")

    st.write("")

    st.button("Change Password")
