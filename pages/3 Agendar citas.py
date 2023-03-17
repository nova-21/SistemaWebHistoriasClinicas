import datetime
import os

import streamlit as st
from sqlalchemy import create_engine

from data.actions.appointment_actions import add_appointment
from data.conection import create_engine_conection
from utilidades.lists import list_encounter_types
from utilidades.vies_utilities import clean, load_logo

load_logo()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True


if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine_conection()


def create_appointment(base):
    with base:
        with st.form(key="appointment_register"):
            patient_id = st.text_input("Cédula del paciente")
            appointment_type = st.radio(
                "Seleccione el tipo de cita",
                (
                    "Primera vez",
                    "Subsecuente",
                ),
            )

            encounter_type = st.selectbox(
                "Tipo de atención",
                list_encounter_types,
                help="Puede escribir aquí para buscar un tipo de atención",
            )
            date = st.date_input("Fecha de la cita (Año/Mes/Día)")
            time = st.time_input("Hora de la cita")
            practitioner_id = st.session_state.practitioner_login_id
            submit = st.form_submit_button(label="Guardar")
        if submit:
            # Convert the input to a datetime object
            time_obj = datetime.datetime.combine(datetime.date.today(), time)
            time_formatted = time_obj.strftime('%H:%M')
            # Convert the datetime object to HH:MM format
            message = add_appointment(
                db_engine=st.session_state.db_engine,
                patient_id=patient_id,
                practitioner_id=practitioner_id,
                appointment_type=appointment_type,
                encounter_type=encounter_type,
                status="booked",
                reason="none",
                date=date,
                time=time_formatted,
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
