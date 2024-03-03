import streamlit as st

from components import sidebar, home, settings, chat, user, content_gen

def main():
    components_info = {
        "Home"		: {"icon": "house", "page": home}, 
        "Chat"	: {"icon": "chat", "page": chat},
        "Settings": {"icon": "gear", "page": settings},
        "User": {"icon": "person-gear", "page": user},
        "Content": {"icon": "body-text", "page": content_gen}        
    }
    
    
    sidebar.show(components_info).render()

if __name__ == "__main__":
    main()