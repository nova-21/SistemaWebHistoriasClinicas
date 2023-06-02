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


def show_header_patient_lookup(header_container):
    header_container.empty()
    with header_container.container():
        img = Image.open("resources/ucuenca.png")
        st.image(img, width=200)
        st.subheader("Búsqueda de pacientes")



def show_header(header_container):
    header_container.empty()
    with header_container.container():
        img = Image.open("resources/ucuenca.png")
        st.image(img, width=200)
        col1, col2, col3 = st.columns([2,1,1])

        col1.subheader("Perfil e historial del paciente")
        col3.subheader("Confidencial")
