import pandas as pd
import streamlit as st
from PIL import Image

membrete = st.empty()
membrete.empty()
contenedor_form = st.empty()
with membrete.container():
    img = Image.open("resources/ucuenca.png")
    st.image(img, width=200)
    st.header("Dirección de Bienestar Universitario")


with contenedor_form:
    with st.form(key="cita"):
        primera=st.radio("Seleccione el tipo de cita",("Cita regular: para pacientes registrados","Primera cita: para pacientes no registrados"))
        paciente = st.text_input("Cédula del paciente")
        fecha = st.date_input("Fecha de la cita")
        hora = st.time_input("Hora de la cita")
        guardar = st.form_submit_button(label="Guardar")

if guardar:
    st.session_state.registrar_cita = False
    contenedor_form.empty()
    st.success("La cita fue creata con éxito")
    st.button("Aceptar")
    # print("La cita con el paciente "+paciente+" se generó para el ", fecha, hora)
    # st.experimental_rerun()
