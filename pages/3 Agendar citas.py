import datetime
import os
import time
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

if "id_for_appointment" not in st.session_state:
    st.session_state.id_for_appointment = ""
if "practitioner_login_id" not in st.session_state:
    st.session_state.practitioner_login_id = "0106785223"


def create_appointment(base):
    with base:
        with st.form(key="appointment_register", clear_on_submit=True):
            if st.session_state.id_for_appointment != "":
                patient_id = st.text_input("Cédula o identificación del paciente", value=st.session_state.id_for_appointment)
            else:
                patient_id = st.text_input("Cédula o identificación del paciente")
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
            hour = st.time_input("Hora de la cita", step=1800) #1800 equals 30 minutes
            practitioner_id = st.session_state.practitioner_login_id
            submit = st.form_submit_button(label="Guardar")

        if submit:
            try:
                if patient_id == "":
                    raise ValueError("La identificación se encuentra vacía")

                # Convert the input to a datetime object
                time_obj = datetime.datetime.combine(datetime.date.today(), hour)
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
                print(message)
                return message
            except:
                st.error("La identificación se encuentra vacía, revise los datos y vuelva a guardar.")
                time.sleep(2)
                st.experimental_rerun()




clean("Registro de citas")
base = st.empty()
message = create_appointment(base)
if message == "Cita registrada con éxito":
    base.empty()
    st.success(message)
    st.session_state.id_for_appointment = ""
    time.sleep(2)
    st.experimental_rerun()

if (
    message
    == "Error con el registro de la cita, revise los datos e intente nuevamente." or message == "El paciente ya cuenta con una cita en esa fecha, seleccione una distinta."
):
    base.empty()
    st.error(message)
    time.sleep(2)
    st.experimental_rerun()

