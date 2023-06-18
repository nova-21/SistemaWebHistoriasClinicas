import streamlit as st

def get_or_create_session_state(key: str, default_value: any):
    """
    Retrieves the value from the Streamlit session state with the given key. If the key doesn't exist,
    initializes it with the default value.

    Args:
        key (str): The key to retrieve or create in the session state.
        default_value (any): The default value to set if the key doesn't exist.

    Returns:
        any: The value associated with the key in the session state.
    """
    if key not in st.session_state:
        st.session_state[key] = default_value
    return st.session_state[key]