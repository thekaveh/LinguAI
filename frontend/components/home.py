import streamlit as st

from utils.logger import log_decorator


@log_decorator
def render():
    # st.title("LinguAI")
    # st.image("./static/LinguAI.png", width=1600)

    st.image("./static/logo.png", width=100)

    st.subheader("Personalized language learning for intermediate learners")

    st.image("./static/different-languages.jpeg", width=704)

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Our Features:")
        st.write("- Dynamic content generation based on your interests and proficiency level.")
        st.write("- Rewrite existing content to match your skill level")
        st.write("- Progress tracking to monitor your improvement.")
    with col2:
        with st.container():
            with st.form(key="login_signup_form"):
                st.subheader("Get Started Today!")
                st.write("<div style='text-align: center;'>Create an account to continue your language learning journey:</div>", unsafe_allow_html=True)
                st.write("")

                register_button = st.form_submit_button("Register")

                st.write("...or if you're already signed up :)")
                login_button = st.form_submit_button("Login")
    
    st.write("")
    
    col1, col2 = st.columns([2, 1])

    with col1:
        st.image("./static/language.jpg")
    with col2:
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
