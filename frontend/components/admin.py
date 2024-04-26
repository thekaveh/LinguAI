# Updated admin.py to include a workaround for confirmation
import streamlit as st
from utils.logger import log_decorator
from services.user_service import UserService
import asyncio


@log_decorator
def render():
    """
    Renders the User List page in the admin component.

    This function displays a table of users with their usernames, emails, and user types.
    It also provides a delete button for each user, allowing the admin to delete a user from the system.

    Raises:
        Exception: If there is an error deleting a user.

    Returns:
        None
    """
    st.title("User List")
    if 'confirm_delete' not in st.session_state:
        st.session_state['confirm_delete'] = None


    users = asyncio.run(UserService.list())
    if users:
        cols = st.columns([3, 4, 3, 2])
        cols[0].subheader("Username")
        cols[1].subheader("Email")
        cols[2].subheader("User Type")
        for user in users:
            cols = st.columns([3, 4, 3, 2])
            cols[0].write(user.username)
            cols[1].write(user.email)
            cols[2].write(user.user_type)
            delete_key = f"delete_{user.username}"
            if cols[3].button("🗑️", key=delete_key):
                st.session_state['confirm_delete'] = user.username


    if st.session_state['confirm_delete']:
        if st.button(f"Confirm delete {st.session_state['confirm_delete']}?"):
            try:
                asyncio.run(UserService.delete_user(st.session_state['confirm_delete']))
                st.success(f"Deleted user '{st.session_state['confirm_delete']}'")
                st.session_state['confirm_delete'] = None
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error deleting user '{st.session_state['confirm_delete']}': {e}")
                st.session_state['confirm_delete'] = None