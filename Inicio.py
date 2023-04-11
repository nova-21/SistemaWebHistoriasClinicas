import datetime
import os
import time

from sqlalchemy import create_engine
from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode
from streamlit_extras.switch_page_button import switch_page
from data.actions.appointment_actions import get_todays_appointments, update_appointment
from data.actions.encounter_actions import get_encounter_activities, add_encounter
from data.actions.practitioner_actions import (
    get_practitioner,
    get_practitioner_by_email,
)
from data.conection import create_engine_conection
from data.create_database import Encounter
from utilidades.time_utilities import get_today
from utilidades.vies_utilities import clean, load_logo
from utilidades.authentication import login
import streamlit as st

st.set_page_config(
    page_title="Ucuenca - Manejo de pacientes", page_icon=load_logo(), layout="wide"
)

if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine_conection()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "practitioner_login_id" not in st.session_state:
    st.session_state.practitioner_login_id = "0106785223"

if "appointment_selected" not in st.session_state:
    st.session_state.appointment_selected = " "

if "submit_cita" not in st.session_state:
    st.session_state.submit_cita = False

clean("Citas del día de hoy")

appointments_history = get_todays_appointments(st.session_state.db_engine)
if len(appointments_history) == 0:
    st.success("No tiene citas pendientes el día de hoy")
builder = GridOptionsBuilder.from_dataframe(appointments_history)
builder.configure_selection(selection_mode="single", use_checkbox=False)
builder.configure_default_column(columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW)
gridoptions = builder.build()

sesion = AgGrid(
    appointments_history,
    gridOptions=gridoptions,
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
    enable_enterprise_modules=False,
)

appointment_selected = sesion["selected_rows"]

def mark_appointment():
    update_appointment(
        db_engine=st.session_state.db_engine,
        status="no-atendida",
        reason=reason_cancellation,
        date=get_today(),
        patient_id=appointment_selected[0]["Cédula"],
    )
    st.success("Se ha registrado el estado de la cita")
    time.sleep(1)


# Display appointment details and buttons if appointment is selected
if appointment_selected:
    st.session_state.patient_id = appointment_selected[0]["Cédula"]
    if st.session_state.appointment_selected != appointment_selected:
        st.session_state.submit_cita = False

    st.session_state.appointment_selected = appointment_selected

    patients_name = appointment_selected[0]["Paciente"]
    st.subheader("Información de la cita")
    st.write('**Paciente:**',patients_name)

    if get_encounter_activities(st.session_state.db_engine, st.session_state.patient_id) is not None:
        previous_activities = get_encounter_activities(st.session_state.db_engine, st.session_state.patient_id)[0]
        st.write(f"**Actividades enviadas en la sesión anterior:** ", previous_activities)

    # Define button columns and actions
    col1, col2, col3,col4,col5,col6 = st.columns(6, gap="small")
    if col1.button("Iniciar sesión", type="primary", key="in" + patients_name):
        st.session_state.current_view = "Historial"
        new_encounter = Encounter()
        new_encounter.patient_id = st.session_state.patient_id
        new_encounter.date = datetime.datetime.today()
        new_encounter.encounter_type = appointment_selected[0]["Tipo de atención"]
        new_encounter.activities_sent = ""
        new_encounter.diagnostics = ""
        new_encounter.attachments = ""
        new_encounter.topics_boarded = ""
        new_encounter.practitioner_id = "0106785223" # TODO replace for real
        add_encounter(st.session_state.db_engine,new_encounter)
        update_appointment(
            st.session_state.db_engine,
            status="atendida",
            reason="",
            date=get_today(),
            patient_id=st.session_state.patient_id,
        )
        st.session_state.encounter_row_selected = (
            0  # Select the first encounter in the Informacion pacientes view
        )
        st.session_state.previous_page = "inicio"
        switch_page("Información pacientes")
        st.stop()

    if col2.button("Ver paciente", key="ver" + patients_name):
        st.session_state.current_view = "Historial"
        st.session_state.previous_page = "inicio"
        switch_page("Información pacientes")
        st.stop()

    if col3.button("No se realizó", key="falta" + patients_name):
        st.session_state.submit_cita = True

    if st.session_state.submit_cita == True:
        with st.form(key="cancel_appointment"):
            reason_cancellation = st.selectbox(
                "Seleccione el motivo",
                options=(
                    "Ausentismo",
                    "Reagendamiento por el paciente",
                    "Reagendamiento por el tratante",
                ),
            )

            if st.form_submit_button("Guardar", type="primary"):
                mark_appointment()
                st.session_state.submit_cita = False
                st.experimental_rerun()
        with st.sidebar:
            if st.button("❌ Cancelar", type="primary"):
                st.session_state.submit_cita =False
                st.experimental_rerun()

