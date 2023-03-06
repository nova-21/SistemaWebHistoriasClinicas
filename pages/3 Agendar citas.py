import os

import streamlit as st
from sqlalchemy import create_engine

from data.actions.appointment_actions import add_appointment
from data.conection import create_engine_conection
from utilidades.vies_utilities import clean, load_logo

load_logo()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in ==True:

    if "db_engine" not in st.session_state:
        st.session_state.db_engine = create_engine_conection()


    def create_appointment(base):
        with base:
            with st.form(key="appointment_register"):
                appointment_type = st.radio(
                    "Seleccione el tipo de cita",
                    (
                        "Primera vez",
                        "Subsecuente",
                    ),
                )
                patient_id = st.text_input("Cédula del paciente")
                date = st.date_input("Fecha de la cita (Año/Mes/Día)")
                time = str(st.time_input("Hora de la cita"))
                practitioner_id = st.session_state.practitioner_login_id
                submit = st.form_submit_button(label="Guardar")
            if submit:
                message = add_appointment(
                    db_engine=st.session_state.db_engine,
                    patient_id=patient_id,
                    practitioner_id=practitioner_id,
                    appointment_type=appointment_type,
                    status="booked",
                    reason="none",
                    date=date,
                    time=time,
                )
                return message


    clean("Registro de citas")
    base = st.empty()
    message = create_appointment(base)
    if message == "Cita registrada con éxito":
        base.empty()
        st.success(message)
        st.button("Aceptar")
    if (
        message
        == "Error con el registro de la cita, revise los datos e intente nuevamente."
    ):
        base.empty()
        st.error(message)
        st.button("Aceptar")
else:
    clean("Inicie sesión para continuar")
