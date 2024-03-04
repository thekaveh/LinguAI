import logging
import streamlit as st

from components import sidebar, home, settings, chat, user, content_gen, profile

logging.basicConfig(
    level=logging.DEBUG,
    filename="/app/logs/backend-app.log",
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    components_info = {
        "Home": {"icon": "house", "page": home},
        "Chat": {"icon": "chat", "page": chat},
        "Account": {"icon": "person-circle", "page": profile},
        "Settings": {"icon": "gear", "page": settings},
        "User": {"icon": "person-gear", "page": user},
        "Content": {"icon": "body-text", "page": content_gen},
    }

    sidebar.show(components_info).render()


if __name__ == "__main__":
    main()
