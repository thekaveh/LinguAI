# frontend/app.py
import streamlit as st
import requests

BACKEND_URL = "http://backend:8000/"

def get_hello_world():
    response = requests.get(BACKEND_URL)
    if response.ok:
        return response.json()
    else:
        return {"Error": "Failed to fetch data from backend"}

st.title('Hello World Streamlit Frontend')

# Fetch and display data from the backend
data = get_hello_world()
st.write(data)
