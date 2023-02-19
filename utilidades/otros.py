import streamlit as st
from PIL import Image


@st.experimental_memo
def cargar_imagen():
    img = Image.open("./resources/ucuenca-min.png")
    return img


def limpiar(subtitulo):
    membrete = st.empty()
    membrete.empty()
    with membrete.container():
        img = cargar_imagen()
        st.image(img, width=200)
        st.subheader("Dirección de Bienestar Universitario")
        st.markdown("#### "+subtitulo)

def logo_titulo():
    img = Image.open("./resources/favicon.png")
    st.set_page_config(page_title="Ucuenca - Manejo de pacientes", page_icon=img, layout="wide")
