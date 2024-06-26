import streamlit as st

def render():
    """
    Renders the footer notes with a visual style.

    This function generates and displays the footer notes for the LinguAI Inc. website.
    The footer includes the company name and copyright information.

    Returns:
        None
    """
    #st.image("./static/logo.png", width=100)
    # Footer notes rendering with a visual style
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            color: #ffffff;
            background-color: #ff6600;
            padding: 5px;
            display: flex;
            justify-content: space-between;
            z-index: 2; /* Ensure footer is above other content */
        }
        .footer-column {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: left;
            width: 33.33%;
        }
        .footer-column.right {
            align-items: flex-end;
            text-align: center;
            padding-right: 20px;
        }
        .footer-column.center p {
            font-size: 24px;
            font-weight: bold;
            text-align: left;
        }
        .footer-column.right p {
            font-size: 16px;
            font-weight: normal;
        }
        .content {
            z-index: 1; /* Ensure main content is below the footer */
        }
        </style>
        <div class="footer">
            <div class="footer-column left">                
                <!-- Left column intentionally left empty -->
            </div>
            <div class="footer-column center">
                <p>LinguAI Inc.</p>
            </div>
            <div class="footer-column right">
                <p class="copyright">© 2024 LinguAI Inc. All rights reserved.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
