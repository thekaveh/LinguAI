import streamlit as st
from streamlit_option_menu import option_menu

from utils.logger import log_decorator


@log_decorator
def show(pages):
    with st.sidebar:
        selected = option_menu(
            default_index=0,
            menu_icon="cast",
            menu_title="LinguAI",
            orientation="vertical",
            options=list(pages.keys()),
            icons=[pages[option]["icon"] for option in pages.keys()],
        )

        return pages[selected]["page"]
