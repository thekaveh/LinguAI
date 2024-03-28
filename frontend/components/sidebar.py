import streamlit as st
from streamlit_option_menu import option_menu
import asyncio

from utils.logger import log_decorator
from services.user_service import UserService
from services.state_service import StateService
from schema.authentication import AuthenticationRequest, AuthenticationResponse


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
        state_service = StateService.instance()
        # Check if the user is authenticated
        if state_service.username is not None:
            # Visually separate the logout button from the menu
            if st.button("Logout", type="primary", use_container_width=True):
                # Perform logout actions: Reset the authentication state
                state_service.clear_session_state()
                st.experimental_rerun()
        else:
            # Display the login form only if the user is not authenticated
            st.write("---")
            st.subheader("Login to LinguAI")

            username = st.text_input("Username", placeholder="Your Username")
            password = st.text_input(
                "Password", placeholder="Your Password", type="password"
            )

            if st.button("Login", type="primary", use_container_width=True) or (
                username and password
            ):
                # Placeholder for your authentication logic
                # Replace the next line with your authentication check
                # authenticated = username == "admin" and password == "password"  # Example condition
                auth_request = AuthenticationRequest(
                    username=username, password=password
                )
                auth_response = asyncio.run(UserService.authenticate(auth_request))

                if auth_response.status:
                    state_service.username = auth_response.username
                    st.experimental_rerun()
                else:
                    st.error(auth_response.message)

            st.markdown(
                f"""Don't have an account?                         
                        click  <b>New User Registration</b>""",
                unsafe_allow_html=True,
            )
            # register.render()

        return pages[selected]["page"]
