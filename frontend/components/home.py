import streamlit as st

from utils.logger import log_decorator


@log_decorator
def render():
    st.title("LinguAI")
    # st.image("./static/LinguAI.png", width=1600)
    st.subheader("Personalized language learning for intermediate learners")

    col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(9)

    with col4:
        st.image("./static/translate.svg")
    with col5:
        st.image("./static/book.svg")
    with col6:
        st.image("./static/chat-text.svg")

    st.write("")
    st.write("")
    st.write("")

    with st.container():
        with st.form(key="login_signup_form"):
            st.write("Create an account now to get started!")

            register_button = st.form_submit_button("Register")
            login_button = st.form_submit_button("Login")

    styling = """
		<style>
			[data-testid="stForm"] {
				background: #c1e4ff;
				width: 50%;
			}
			[data-testid="stForm"] div div div {
				display: flex;
				flex-direction: column;
				align-items: center;
			}
		</style>
	"""
    st.write(styling, unsafe_allow_html=True)
