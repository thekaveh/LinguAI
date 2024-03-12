import streamlit as st

def render():
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
            padding: 10px;
            display: flex;
            justify-content: space-between;
            z-index: 2; /* Ensure footer is above other content */
        }
        .footer-column {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
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
        }
        .footer-column.right p {
            font-size: 12px;
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
                <p class="copyright">© 2024 LinguAI Inc. All rights reserved. Unauthorized use and/or duplication of this material without express and written permission from this site’s author and/or owner is strictly prohibited.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
