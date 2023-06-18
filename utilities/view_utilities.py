import streamlit as st
from PIL import Image


@st.cache_data
def load_image():
    """
    Loads and returns an image from the specified path.

    Returns:
        PIL.Image.Image: The loaded image.
    """
    img = Image.open("./static_resources/ucuenca-min.png")
    return img


def clean(subheader, instructions=""):
    """
    Displays a clean header section with an image, subheader, and optional instructions.

    Args:
        subheader (str): The subheader text to display.
        instructions (str, optional): Additional instructions to display. Defaults to "".
    """
    header_section = st.empty()
    header_section.empty()
    with header_section.container():
        img = load_image()
        st.image(img, width=200)
        st.subheader("Dirección de Bienestar Universitario")
        st.markdown("#### " + subheader)
        if instructions != "":
            st.markdown("###### " + instructions)


def load_logo():
    """
    Loads and returns the logo image.

    Returns:
        PIL.Image.Image: The loaded logo image.
    """
    img = Image.open("./static_resources/favicon.png")
    return img


def show_header_patient_lookup(header_container):
    """
    Displays the header section for patient lookup.

    Args:
        header_container: The container for the header section.
    """
    header_container.empty()
    with header_container.container():
        img = Image.open("static_resources/ucuenca.png")
        st.image(img, width=200)
        st.subheader("Búsqueda de pacientes")


def show_header(header_container):
    """
    Displays the header section.

    Args:
        header_container: The container for the header section.
    """
    header_container.empty()
    with header_container.container():
        img = Image.open("static_resources/ucuenca.png")
        st.image(img, width=200)
        col1, col2, col3 = st.columns([2, 1, 1])

        col1.subheader("Perfil e historial del paciente")
        col3.subheader("Confidencial")
