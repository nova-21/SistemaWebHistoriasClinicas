import streamlit as st
from PIL import Image


def limpiar(subtitulo):
    membrete = st.empty()
    membrete.empty()
    with membrete.container():
        img = Image.open("ucuenca.png")
        st.image(img, width=200)
        st.header("Dirección de Bienestar Universitario")
        st.subheader(subtitulo)