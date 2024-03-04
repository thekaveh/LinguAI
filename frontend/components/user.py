import asyncio
import streamlit as st

from utils.logger import log_decorator
from services.user_service import UserService


@log_decorator
def render():
    st.title("User List")

    # Display a button to trigger data fetching
    if st.button("Fetch Users"):
        # Call fetch_users asynchronously
        st.markdown("<hr>", unsafe_allow_html=True)
        # Await the coroutine properly
        # Use asyncio.run() to run the coroutine in a synchronous context
        users = asyncio.run(UserService.list())
        # Display the user list
        # Display the user list in a table format
        if isinstance(users, list):
            if users:
                st.write("### Users:")
                user_data = [
                    {
                        "Username": user.username,
                        "Email": user.email,
                        "User Type": user.user_type,
                    }
                    for user in users
                ]
                st.table(user_data)
            else:
                st.write("No users found.")
        else:
            st.error("Error: Users data is not in the correct format.")
            st.error("Error: Users data is not in the correct format.")
