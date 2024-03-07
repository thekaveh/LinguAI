import streamlit as st
from utils.logger import log_decorator
import requests


# This function sends requests to backend
def authenticate(username, password) -> (bool, str):
    api_url = "http://backend:8000/v1/users/authenticate"
    try:
        response = requests.post(api_url, json={"username": username, "password": password})
        if response.status_code == 200:
            # Authentication successful
            user_name = response.json().get("name", "")
            return True, user_name
        elif response.status_code == 401:
            error_response = response.json()
            print("this is the error response")
            print(error_response)
            error_detail = error_response.get("detail", "Authentication failed.")
            st.error(error_detail)
            return False, None
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return False, None
    
@log_decorator
def render():
    # Initial checks for session state variables
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    st.image("./static/logo.png", width=100)
    st.subheader("Personalized language learning for intermediate learners")
    st.image("./static/different-languages.jpeg", width=704)
    st.write("")


    if not st.session_state["authenticated"]:
        # User is not authenticated; show login or registration option
        col1, col2 = st.columns(2)


        with col1:
            st.subheader("Our Features:")
            st.write("- Dynamic content generation based on your interests and proficiency level.")
            st.write("- Rewrite existing content to match your skill level")
            st.write("- Progress tracking to monitor your improvement.")


        with col2:
            with st.container():
                with st.form(key="login_form"):
                    st.subheader("Get Started Today!")
                    st.write("<div style='text-align: center;'>Login to continue your language learning journey:</div>", unsafe_allow_html=True)
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")

                    login_button = st.form_submit_button("Login")
                    if login_button:
                        authenticated, user_name = authenticate(username, password)
                        if authenticated:
                            st.session_state["authenticated"] = True
                            st.session_state["user_name"] = user_name
                            st.experimental_rerun()

    else:
        # User is authenticated; show the rest of the content
        st.write(f"Welcome back, {st.session_state.get('user_name')}!")
        # Add the rest of your application's components here


    col1, col2 = st.columns([2, 1])


    with col1:
        if not st.session_state["authenticated"]:
            st.image("./static/language.jpg")


    with col2:
        if not st.session_state["authenticated"]:
            st.write("_LinguAI provides customized language learning for learners who are looking to take the next step to improve their comprehension after learning the basics. Sign up today to continue your learning and try out our personalized features!_")


    st.markdown("---")
    st.write("© 2024 LinguAI. All rights reserved.")


    styling = """
        <style>
            [data-testid="stForm"] {
                background: #E8DAB2;
                width: 100%;
            }
            [data-testid="stForm"] div div div {
                display: flex;
                flex-direction: column;
                align-items: center;
            }
        </style>
    """
    st.write(styling, unsafe_allow_html=True)