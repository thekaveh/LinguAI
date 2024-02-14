import streamlit as st

from streamlit_option_menu import option_menu

from components import home, settings, chat

def show():
    pages = {
        "Home": {"icon": "house", "page": home},
        "Chat": {"icon": "chat", "page": chat},
        "Settings": {"icon": "gear", "page": settings},
    }

    with st.sidebar:
        selected = option_menu(
            menu_title="LinguAI",
            options=list(pages.keys()),
            icons=[pages[option]["icon"] for option in pages.keys()],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
        )


    pages[selected]["page"].render()
