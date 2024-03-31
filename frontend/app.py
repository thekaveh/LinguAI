import streamlit as st
from core.config import Config
from utils.logger_config import setup_global_logging
from services.user_service import UserService
from services.state_service import StateService
from components import (
    sidebar, 
    home, 
    settings, 
    chat, 
    admin, 
    content_gen, 
    profile, 
    interest_selection, 
    rewrite_content, 
    review_writing , 
    foot_notes,
    header,
    register,
)
import asyncio

# Setup global logging with a specific logger name
setup_global_logging(
    logger_name=Config.FRONTEND_LOGGER_NAME,
    log_filename=Config.FRONTEND_LOG_FILE,
    log_level=Config.FRONTEND_LOG_LEVEL,
)

def main():
    header.render()
    state_service = StateService.instance()

    components_info = {
        "Home": {"icon": "house", "page": home},
        "New User Registration": {"icon": "person-plus", "page": register}
    }
    
    if state_service.username is not None:
        user = asyncio.run(UserService.get_user_by_username(state_service.username))

        if user.user_type == "admin":
            components_info = {
                "Home": {"icon": "house", "page": home},
                "Rewrite Content": {"icon": "pen", "page": rewrite_content},
                "Review Writing": {"icon": "pencil-square", "page": review_writing},               
                "Content Reading": {"icon": "body-text", "page": content_gen},            
                "Chat": {"icon": "chat", "page": chat},
                "Profile": {"icon": "person-circle", "page": profile},
                "Admin": {"icon": "person-gear", "page": admin},
                "Settings": {"icon": "gear", "page": settings},
            }
        else:
            components_info = {
                "Home": {"icon": "house", "page": home},
                "Rewrite Content": {"icon": "pen", "page": rewrite_content},
                "Review Writing": {"icon": "pencil-square", "page": review_writing},               
                "Content Reading": {"icon": "body-text", "page": content_gen},            
                "Chat": {"icon": "chat", "page": chat},
                "Profile": {"icon": "person-circle", "page": profile},
                "Settings": {"icon": "gear", "page": settings},
            }
            
    selected_page = sidebar.show(components_info)
    # Assuming sidebar.show() updates `st.session_state.current_page` based on the selected page
    selected_page.render()

    # Conditionally render foot_notes based on the current page
    if selected_page != chat:
        foot_notes.render()

    
if __name__ == "__main__":
    main()