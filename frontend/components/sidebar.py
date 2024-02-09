import streamlit as st
from streamlit_option_menu import option_menu

from pages import home, settings

def fetch_sidebar_selection():
    """Create a VSCode-styled sidebar using streamlit-option-menu with enhanced styling."""
    # Define the options and corresponding icons
    pages = {
        "Home": {"icon": "house", "page": home},
        # "Search": {"icon": "search"},
        # "Files": {"icon": "folder"},
        "Settings": {"icon": "gear", "page": settings},
        # Add more menu items as needed
    }
    
    with st.sidebar:
        # Create the option menu with customized styles
        selected = option_menu(
            menu_title=None,  # No title for a VSCode-like appearance
            options=list(pages.keys()),
            icons=[pages[option]["icon"] for option in pages.keys()],
            menu_icon="cast",  # Optional: icon for the menu itself
            default_index=0,  # Default to the first item
            orientation="vertical",
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "orange", "font-size": "20px"},
                "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#4682B4"},
                "nav-link-selected": {"background-color": "#4682B4"},
            }
        )
        
        return pages[selected]["page"]