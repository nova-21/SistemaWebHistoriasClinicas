import os

import streamlit as st
from sqlalchemy import create_engine

from data.actions.appointment_actions import add_appointment
from utilidades.vies_utilities import clean, load_logo

load_logo()

if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine(os.environ.get("DATABASE"))


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
            practitioner_id = (
                "0106785223"  # TODO change to read practitioner session.state
            )
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
