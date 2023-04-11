import streamlit as st
from PIL import Image


@st.cache_data
def load_image():
    img = Image.open("./resources/ucuenca-min.png")
    return img


def clean(subheader, instructions=""):
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
    img = Image.open("./resources/favicon.png")
    return img


def show_header(header_container):
    header_container.empty()
    with header_container.container():
        img = Image.open("resources/ucuenca.png")
        st.image(img, width=200)
        st.subheader("Perfil e historial del paciente")
