import streamlit as st

from core.config import Config
from utils.logger_config import setup_global_logging
from components import sidebar, home, settings, chat, user, content_gen, profile

# Setup global logging with a specific logger name
setup_global_logging(
    logger_name=Config.FRONTEND_LOGGER_NAME,
    log_filename=Config.FRONTEND_LOG_FILE,
    log_level=Config.FRONTEND_LOG_LEVEL,
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
