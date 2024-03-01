import streamlit as st
import asyncio
from services.user_service import UserService
from models.schema.user import User
from services.address_service import AddressService 

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
    
    # Add a button to fetch addresses
    if st.button("Fetch Addresses"):
        st.markdown("<hr>", unsafe_allow_html=True)
        addresses = asyncio.run(AddressService.list())     

        # Display the address list
        # Display the address list in a table format
        if isinstance(addresses, list):
            if addresses:
                st.write("### Addresses:")
                address_data = [{"Street": address.street, "City": address.city, "State": address.state, "Country": address.country} for address in addresses]
                st.table(address_data)
            else:
                st.write("No addresses found.")
        else:
            st.error("Error: Addresses data is not in the correct format.")
# Run the render function
#render()