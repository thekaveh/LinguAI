import streamlit as st
from core.config import Config
from utils.logger_config import setup_global_logging

from services.state_service import StateService
from components import sidebar, home, settings, chat, user, content_gen, profile, interest_selection, rewrite_content, review_writing

# Setup global logging with a specific logger name
setup_global_logging(
    logger_name=Config.FRONTEND_LOGGER_NAME,
    log_filename=Config.FRONTEND_LOG_FILE,
    log_level=Config.FRONTEND_LOG_LEVEL,
)

def main():
    state_service = StateService.instance()

    components_info = {
         "Home": {"icon": "house", "page": home},
    }
    
    if state_service.username is not None:
        components_info = {
            "Home": {"icon": "house", "page": home},
            "Interest Selection": {"icon": "palette", "page": interest_selection},
            "Rewrite Content": {"icon": "pen", "page": rewrite_content},
            "Review Writing": {"icon": "pencil-square", "page": review_writing},               
            "Content Reading": {"icon": "body-text", "page": content_gen},            
            "Chat": {"icon": "chat", "page": chat},
            "Account": {"icon": "person-circle", "page": profile},
            "User": {"icon": "person-gear", "page": user},
            "Settings": {"icon": "gear", "page": settings},
        }

    sidebar.show(components_info).render()
    
if __name__ == "__main__":
    main()
