import datetime
import time
from typing import Dict

import streamlit as st

from data.repositories.AppointmentRepository import add_appointment
from data.database_connection import create_engine_conection
from utilities.lists import list_encounter_types
from utilities.view_utilities import clean, load_logo


def get_or_create_session_state(key: str, default_value: any):
    """
    Retrieves the value from the Streamlit session state with the given key. If the key doesn't exist,
    initializes it with the default value.

    Args:
        key (str): The key to retrieve or create in the session state.
        default_value (any): The default value to set if the key doesn't exist.

    Returns:
        any: The value associated with the key in the session state.
    """
    if key not in st.session_state:
        st.session_state[key] = default_value
    return st.session_state[key]


def create_appointment(base, db_engine):
    """
    Creates an appointment form and handles the submission.

    Args:
        base: The base Streamlit element to display the form.
        db_engine: The database engine connection.

    Returns:
        str: A message indicating the status of the appointment creation.
    """
    with base:
        with st.form(key="appointment_register", clear_on_submit=True):
            patient_id = st.text_input("Cédula o identificación del paciente", value=get_or_create_session_state("id_for_appointment", ""))
            appointment_type = st.radio("Seleccione el tipo de cita", ("Primera vez", "Subsecuente"))
            encounter_type = st.selectbox("Tipo de atención", list_encounter_types, help="Puede escribir aquí para buscar un tipo de atención")
            date = st.date_input("Fecha de la cita (Año/Mes/Día)")
            hour = st.time_input("Hora de la cita", step=1800)  # 1800 equals 30 minutes
            practitioner_id = get_or_create_session_state("practitioner_login_id", "")
            submit = st.form_submit_button(label="Guardar", type="primary")

        if submit:
            try:
                if patient_id == "":
                    raise ValueError("La identificación se encuentra vacía")

                # Convert the input to a datetime object
                time_obj = datetime.datetime.combine(datetime.date.today(), hour)
                time_formatted = time_obj.strftime("%H:%M")

                # Convert the datetime object to HH:MM format
                message = add_appointment(
                    db_engine=db_engine,
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
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error("Error con el registro de la cita, revise los datos e intente nuevamente.")
                st.exception(e)


def main():
    """
    The main function that runs the Streamlit application.
    """
    load_logo()
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = True

    db_engine = get_or_create_session_state("db_engine", create_engine_conection())
    user_info = get_or_create_session_state("user_info", {})

    if user_info:
        clean("Registro de citas")
        base = st.empty()
        message = create_appointment(base, db_engine)
        if message == "Cita registrada con éxito":
            base.empty()
            st.success(message)
            get_or_create_session_state("id_for_appointment", "")
            time.sleep(2)
            st.experimental_rerun()

        elif message in ("El paciente ya cuenta con una cita en esa fecha, seleccione una distinta.", "El paciente no se encuentra registrado"):
            base.empty()
            st.error(message)
            time.sleep(2)
            st.experimental_rerun()

    else:
        clean("Por favor inicie sesión para continuar")


if __name__ == "__main__":
    main()
