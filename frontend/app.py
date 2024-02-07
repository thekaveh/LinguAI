import os
import requests
import streamlit as st

BACKEND_ENDPOINT = os.environ.get("BACKEND_ENDPOINT", "http://backend:8000/")

st.write(os.environ.get("BACKEND_ENDPOINT"))

def get_hello_world():
    response = requests.get(BACKEND_ENDPOINT)
    if response.ok:
        return response.json()
    else:
        return {"Error": "Failed to fetch data from backend"}

st.title('Hello World Streamlit Frontend XXX')

# Fetch and display data from the backend
data = get_hello_world()
st.write(data)