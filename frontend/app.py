import streamlit as st

from components import sidebar, home, settings, chat, user

def main():
    components_info = {
        "Home"		: {"icon": "house", "page": home}, 
        "Chat"	: {"icon": "chat", "page": chat},
        "Settings": {"icon": "gear", "page": settings},
        "User": {"icon": "person-gear", "page": user},
        "Content": {"icon": "body-text", "page": user}        
    }
    
    
    sidebar.show(components_info).render()

if __name__ == "__main__":
    main()