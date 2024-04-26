import asyncio
import streamlit as st
from streamlit_option_menu import option_menu

from utils.logger import log_decorator
from services.user_service import UserService
from services.state_service import StateService
from schema.authentication import AuthenticationRequest
from services.notification_service import NotificationService


@log_decorator
def show(pages):
    """
    Displays the sidebar with options for the user to select.

    Args:
        pages (dict): A dictionary containing the available pages and their corresponding information.

    Returns:
        tuple: A tuple containing the selected option and the corresponding page.
    """
    with st.sidebar:
        state_service = StateService.instance()

        if st.session_state.get("switch_button", False):
            manual_select = (state_service.last_visited + 1) % 8
        else:
            manual_select = None

        selected = option_menu(
            default_index=0,
            menu_title="LinguAI",
            orientation="vertical",
            options=list(pages.keys()),
            menu_icon="globe-americas",
            icons=[pages[option]["icon"] for option in pages.keys()],
            manual_select=manual_select,
        )

        # Check if the user is authenticated
        if state_service.username is not None:
            # Visually separate the logout button from the menu
            if st.button("Logout", type="primary", use_container_width=True):
                # Perform logout actions: Reset the authentication state
                state_service.reset_fields()
                state_service.just_logged_out = True
                st.rerun()
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
                    state_service.just_logged_in = True
                    st.rerun()
                else:
                    NotificationService.failure(message=auth_response.message)

                    st.error(auth_response.message)

            st.markdown(
                """Don't have an account?                         
                        click  <b>New User Registration</b>""",
                unsafe_allow_html=True,
            )

        return selected, pages[selected]["page"]
