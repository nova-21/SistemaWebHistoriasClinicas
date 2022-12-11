
import streamlit as st
from PIL import Image

membrete = st.empty()

def limpiar():
    membrete.empty()
    with membrete.container():
        img = Image.open("ucuenca.png")
        st.image(img, width=200)
        st.header("Departamento de Bienestar Universitario")

limpiar()

st.subheader("Bienvenido al sistema de gestión de historia clínica psicológica")

