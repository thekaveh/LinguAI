import streamlit as st

from streamlit_option_menu import option_menu

from components import home, settings, chat

def show():
    pages = {
		"Home": {"icon": "house", "page": home},
		"Chat": {"icon": "chat", "page": chat},
		"Settings": {"icon": "gear", "page": settings}
	}

    with st.sidebar:
        # st.markdown(f"""
		# 	<a href="/" style="color:black;text-decoration: none;">
		# 		<div style="display:table;margin-top:-14rem;margin-left:0%;">
        #             <span style="font-size: 2em; color: white">LinguAI</span>
		# 			<span style="font-size: 0.8em; color: grey">&nbsp;&nbsp;v1.0.0</span>
		# 			<br>
		# 			<span style="font-size: 0.8em; color: grey">Your AI-powered Language Learning Awesomeness!</span>
		# 		</div>
		# 	</a>
		# 	<br>
		# 		""", unsafe_allow_html=True)

        selected = option_menu(
            menu_title="LinguAI",
            options=list(pages.keys()),
            icons=[pages[option]["icon"] for option in pages.keys()],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
            # styles={
            #     "container": {"padding": "0!important", "background-color": "transparent"},
            #     "icon": {"color": "orange", "font-size": "20px"},
            #     "nav-link": {"font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "#4682B4"},
            #     "nav-link-selected": {"background-color": "#4682B4"},
            # }
        )

    pages[selected]["page"].render()