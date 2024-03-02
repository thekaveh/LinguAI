import streamlit as st

def render():
	st.title("Profile")

	st.image("./static/profile.png", width=225)

	st.write("Name")

	st.write("Username")

	st.write("Comprehension Level")

	st.write("Other Information")

	st.button("Change Password")
	
 