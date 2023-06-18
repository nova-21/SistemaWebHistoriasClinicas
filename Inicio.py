import datetime
import os
import time
from auth0_component import login_button
from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode
from streamlit_extras.switch_page_button import switch_page
from data.repositories.AppointmentRepository import get_todays_appointments, update_appointment
from data.repositories.EncounterRepository import add_encounter_object
from data.repositories.PractitionerRepository import (
    verify_practitioner,
)
from data.database_connection import create_engine_conection
from data.database_declaration import Encounter
from utilities.time_utilities import get_today
from utilities.view_utilities import clean, load_logo
import streamlit as st

# Setting Streamlit page configuration
st.set_page_config(
    page_title="Ucuenca - Manejo de pacientes",
    page_icon=load_logo(),
    layout="wide"
)

# Initializing session state variables, if these aren't initialized Streamlit raises errors at run
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine_conection()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "practitioner_login_id" not in st.session_state:
    st.session_state.practitioner_login_id = ""

if "appointment_selected" not in st.session_state:
    st.session_state.appointment_selected = " "

if "submit_cita" not in st.session_state:
    st.session_state.submit_cita = False

if "id_for_appointment" not in st.session_state:
    st.session_state.id_for_appointment = ""

if "practitioner_position" not in st.session_state:
    st.session_state.practitioner_position = ""


# Auth0 credentials
clientId = "TeVibn7noxsTqxmqK1L8QGo2NDwiPb8S"#os.environ.get("clientId")
domain = "dev-olcsmgnyz0patatu.us.auth0.com"#os.environ.get("domain")

# Checking if user information is available in the session state
if st.session_state.user_info == {}:
    clean("Por favor inicie sesión para continuar")
    user_info = login_button(clientId=clientId, domain=domain)
    if user_info:
        auth, practitioner_id, practitioner_position = verify_practitioner(st.session_state.db_engine, user_info.get("email"))
        if auth == "Access authorized":
            st.session_state.practitioner_login_id = practitioner_id
            st.session_state.practitioner_position = practitioner_position
            st.session_state.user_info = user_info
            st.experimental_rerun()
        if auth == "Access denied":
            st.error("No se encuentra registrado, recarge la página e intente de nuevo")

# If user information is available, display today's appointments
if st.session_state.user_info:
    clean("Citas del día de hoy")
    appointments_history = get_todays_appointments(st.session_state.db_engine, st.session_state.practitioner_login_id)
    if len(appointments_history) == 0:
        st.success("No tiene citas pendientes el día de hoy")

    # Configure the grid options for displaying appointments
    builder = GridOptionsBuilder.from_dataframe(appointments_history)
    builder.configure_selection(selection_mode="single", use_checkbox=False)
    builder.configure_default_column(
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW
    )
    other_options = {"suppressColumnVirtualisation": True}
    builder.configure_grid_options(**other_options)
    gridoptions = builder.build()

    # Display the appointments using AgGrid
    sesion = AgGrid(
        appointments_history,
        gridOptions=gridoptions,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
        enable_enterprise_modules=False,
    )

    appointment_selected = sesion["selected_rows"] # Obtains the data from the appointment selected on the AgGrid table

    if appointment_selected:
        st.session_state.patient_id = appointment_selected[0]["Cédula"]
        if st.session_state.appointment_selected != appointment_selected:
            st.session_state.submit_cita = False

        st.session_state.appointment_selected = appointment_selected

        patients_name = appointment_selected[0]["Paciente"]
        st.subheader("Información de la cita")
        st.write("**Paciente:**", patients_name)

        # Buttons for different actions related to the selected appointment
        # There's 5 columns, but only 3 are used, col4 and col5 are only to fill the space and bring the buttons together
        col1, col2, col3, col4, col5 = st.columns(5, gap="small")

        # Button to start the session for the selected appointment
        if col1.button("Comenzar sesión", type="primary", key="in" + patients_name):
            st.session_state.current_view = "Historial"
            new_encounter = Encounter()
            new_encounter.patient_id = st.session_state.patient_id
            new_encounter.date = datetime.datetime.today()
            new_encounter.encounter_type = appointment_selected[0]["Tipo de atención"] # Select the first encounter in the Informacion pacientes view
            new_encounter.diagnostics = ""
            new_encounter.attachments = ""
            new_encounter.topics_boarded = ""
            new_encounter.practitioner_id = st.session_state.practitioner_login_id
            add_encounter_object(st.session_state.db_engine, new_encounter)
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
            st.session_state.edit_encounter = True
            st.session_state.previous_page = "inicio"
            switch_page("Historia clínica")
            st.stop()

        # Button to explore the selected patient's details
        if col2.button("Explorar paciente", key="ver" + patients_name):
            st.session_state.current_view = "Historial"
            st.session_state.previous_page = "inicio"
            switch_page("Historia clínica")
            st.stop()

        # Button to mark the appointment as absent/cancelled
        if col3.button("Ausentismo/Cancelar", key="falta" + patients_name):
            st.session_state.submit_cita = True


        # Form for submitting cancellation reasons if the appointment is marked as absent/cancelled
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
                    update_appointment(
                        db_engine=st.session_state.db_engine,
                        status="no_atendida",
                        reason=reason_cancellation,
                        date=get_today(),
                        patient_id=appointment_selected[0]["Cédula"],
                    )
                    st.session_state.submit_cita = False
                    st.success("Se ha registrado el estado de la cita")
                    time.sleep(1)
                    st.experimental_rerun()

            with st.sidebar:
                # Button to cancel the cancellation form
                if st.button("❌ Cancelar", type="primary"):
                    st.session_state.submit_cita = False
                    st.experimental_rerun()
