import os

import pandas as pd
import streamlit as st
from PIL import Image
from sqlalchemy import create_engine
from st_aggrid import GridOptionsBuilder, AgGrid
from streamlit_extras.switch_page_button import switch_page

from data.actions.appointment_actions import get_todays_appointments
from utilidades.vies_utilities import clean, load_logo

st.set_page_config(
    page_title="Ucuenca - Manejo de pacientes", page_icon=load_logo(), layout="wide"
)

if "registrar_cita" not in st.session_state:
    st.session_state.registrar_cita = False

if "appointment_selected" not in st.session_state:
    st.session_state.appointment_selected = " "

if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine(os.environ.get("DATABASE"))

clean("Citas del día de hoy")

historial = get_todays_appointments(st.session_state.db_engine)
tabla = historial
builder = GridOptionsBuilder.from_dataframe(tabla)
builder.configure_selection(selection_mode="single", use_checkbox=False)
gridoptions = builder.build()

sesion = AgGrid(
    tabla,
    gridOptions=gridoptions,
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=False,
)

appointment_selected = sesion["selected_rows"]

if appointment_selected:
    nombre = appointment_selected[0]["Nombre"] + appointment_selected[0]["Apellido"]
    st.subheader("Información de la cita")
    st.write(f"**Tareas enviadas:** ")
    st.write("Ejercicios de respiración. Realizar una lista de actividades.")
    col1, col2, col3, col4, col5 = st.columns(5, gap="small")
    col1.button("Iniciar sesión", type="primary", key="in" + nombre)
    col2.button("Ver paciente", key="ver" + nombre)
    col3.button("Reagendar", key="rea" + nombre)
    col4.button("No asistió", key="falta" + nombre)
    col5.button("Cancelar", key="can" + nombre)

    if st.session_state["in" + nombre]:
        st.session_state.current_view = "Historial"
        st.session_state.patient_id = appointment_selected[0]["Cédula"]
        st.session_state.appointment_selected = 0
        switch_page("Información pacientes")
        st.stop()

lista_personas = []

# tabla = tabla.values.tolist()
# for cita in tabla:
#     hora = cita[0]
#     nombre = cita[1] + " " +cita[2]
#     telefono = cita[3]
#     # label = ":red[" + str(hora) + "]" + " " + nombre
#     label = f"**{hora}** {nombre} **{telefono}**"
#     with st.expander(label=label):
#         tabla_detalles = historial[['Teléfono', 'Facultad/Dependencia', 'Carrera']]
#         st.dataframe(tabla_detalles)
#         st.markdown("###### Tareas enviadas en la sesión anterior:")
#         st.write("Ejercicios de respiración. Realizar una lista de actividades.")
#
#         # iniciar, ver, reagendar, ausentismo, cancelar = st.columns(5)
#         # with iniciar:
#         #     st.button("Iniciar sesión",type="primary", key=label+"iniciar")
#         # with ver:
#         #     st.button("Ver paciente", type="secondary", key=label+"ver")
#         # with reagendar:
#         #     st.button("Reagendar cita", key=label+"reagendar")
#         # with ausentismo:
#         #     st.button("Marcar ausentismo", key=label+"ausentismo")
#         # with cancelar:
#         #     st.button("Cancelar cita", key=label+"cancelar")
#
#         # page = st_btn_select(
#         #     # The different pages
#         #     ('Iniciar sesión', 'Ver paciente', 'Reagendar cita', 'Marcar ausentismo', 'Cancelar cita'),
#         #
#         #     # You can pass a formatting function. Here we capitalize the options
#         #     format_func=lambda name: name.capitalize(),
#         #     key=label,
#         # )
#         col1, col2, col3, col4, col5 = st.columns(5, gap="small")
#         col1.button(
#             "Iniciar sesión", type="primary", key="in" + nombre.replace(" ", "")
#         )
#         col2.button("Ver paciente", key="ver" + nombre)
#         col3.button("Reagendar", key="rea" + nombre)
#         col4.button("No asistió", key="falta" + nombre)
#         col5.button("Cancelar", key="can" + nombre)
#         lista_personas.append("in" + nombre.replace(" ", ""))
#
# for persona in lista_personas:
#     if st.session_state[persona] == True:
#         st.session_state.pagina = "Historial"
#         st.session_state.cedula = "123456789"
#         st.session_state.appointment_selected = 0
#         switch_page("Información pacientes")
#         break

# hasta aqui
