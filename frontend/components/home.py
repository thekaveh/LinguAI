import streamlit as st

def render():
	st.title("LinguAI")
	# st.image("./static/LinguAI.png", width=1600)
	st.header("Personalized language learning for intermediate learners")

	col1, col2, col3 = st.columns(3)

	with col1:
		st.image("./static/translate.svg")
	with col2:
		st.image("./static/book.svg")
	with col3:
		st.image("./static/chat-text.svg")
	
	st.write("")
	with st.container():
			st.write("Create an account now to get started!")
			
			register_button = st.button("Register")
			login_button = st.button("Login")
	

	# st.markdown(
	# 	"""
	# 	<style>
	# 		div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlockBorderWrapper"] div[class="st-emotion-cache-1wmy9hl e1f1d6gn1"] div[data-testid="stVerticalBlock"] {
	# 			background-color: #c1e4ff;
	# 			padding: 10px;
	# 			border-radius: 10px;
	# 			display: flex;
	# 			flex-direction:column;
	# 			align-items:center;
	# 		}
	# 	</style>
	# 	""",
	# 	unsafe_allow_html=True,
	# )




