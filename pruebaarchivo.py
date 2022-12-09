import streamlit_google_oauth as oauth
import streamlit as st

login_info = oauth.login(
        client_id="418217949250-26re6hs241ls4v3eu3l73i433v53v6mo.apps.googleusercontent.com",
        client_secret="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",
        redirect_uri="http://localhost:8501",
        login_button_text="Continue with Google",
        logout_button_text="Logout",
    )

if login_info:
        user_id, user_email = login_info
        st.write(f"Welcome {user_email}")
else:
        st.write("Please login")
















