import streamlit as st
import asyncio
from services.user_service import UserService
from models.schema.user import User

def render():
    st.title("User List")

    # Display a button to trigger data fetching
    if st.button("Fetch Users"):
        # Call fetch_users asynchronously
        st.markdown("<hr>", unsafe_allow_html=True)
        users = asyncio.run(UserService.list())     

        # Display the user list
        # Display the user list in a table format
        if isinstance(users, list):
            if users:
                st.write("### Users:")
                user_data = [{"Username": user.username, "Email": user.email, "User Type": user.user_type} for user in users]
                st.table(user_data)
            else:
                st.write("No users found.")
        else:
            st.error("Error: Users data is not in the correct format.")
# Run the render function
#render()