import time
import streamlit as st

cont = st.empty()
cont.empty()
time.sleep(0.01)
with cont.container():
    info, info2, info3 = st.tabs(["Info", "Info2", "Info3"])
    with info:
        st.subheader("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua")
    with info3:
        st.subheader("Title: " )
        st.markdown("**Select the option:**")
        st.checkbox("Option 2")
        st.checkbox("Option 1")


