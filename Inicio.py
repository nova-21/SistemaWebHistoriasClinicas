import os

import streamlit as st
from sqlalchemy import create_engine
from st_aggrid import GridOptionsBuilder, AgGrid
from streamlit_extras.switch_page_button import switch_page
from data.actions.appointment_actions import get_todays_appointments, update_appointment
from data.actions.practitioner_actions import get_practitioner, get_practitioner_by_email
from utilidades.vies_utilities import clean, load_logo
import streamlit_google_oauth as oauth
from utilidades.authentication import login
import streamlit as st

st.set_page_config(
    page_title="Ucuenca - Manejo de pacientes", page_icon=load_logo(), layout="wide"
)

if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine(os.environ.get("DATABASE"))

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False



if st.session_state.logged_in == True:
    with st.sidebar:
        login_info = login(
        client_id="418217949250-26re6hs241ls4v3eu3l73i433v53v6mo.apps.googleusercontent.com",
        client_secret="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",
        redirect_uri="http://localhost:8501",
        login_button_text="Iniciar sesión",
        logout_button_text="Cerrar sesión",
        )
    if "appointment_selected" not in st.session_state:
        st.session_state.appointment_selected = " "

    clean("Citas del día de hoy")

    appointments_history = get_todays_appointments(st.session_state.db_engine)
    builder = GridOptionsBuilder.from_dataframe(appointments_history)
    builder.configure_selection(selection_mode="single", use_checkbox=False)
    gridoptions = builder.build()

    sesion = AgGrid(
        appointments_history,
        gridOptions=gridoptions,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
    )

    appointment_selected = sesion["selected_rows"]


    # Display appointment details and buttons if appointment is selected
    if appointment_selected:
        patients_name = appointment_selected[0]["Nombre"] + appointment_selected[0]["Apellido"]
        st.subheader("Información de la cita")
        st.write(f"**Actividades enviadas en la sesión anterior:** ")
        st.write("Ejercicios de respiración. Realizar una lista de actividades.") # TODO Cambiar por una query que reciba la ultima sesion del paciente

        # Define button columns and actions
        col1, col2, col3, col4, col5 = st.columns(5, gap="small")
        if col1.button("Iniciar sesión", type="primary", key="in" + patients_name):
            st.session_state.current_view = "Historial"
            st.session_state.patient_id = appointment_selected[0]["Cédula"]
            st.session_state.encounter_row_selected = 0 # Select the first encounter in the Informacion pacientes view
            st.session_state.previous_page = "inicio"
            switch_page("Información pacientes")
            st.stop()
        if col2.button("Ver paciente", key="ver" + patients_name):
            st.session_state.current_view = "Historial"
            st.session_state.patient_id = appointment_selected[0]["Cédula"]
            st.session_state.previous_page = "inicio"
            switch_page("Información pacientes")
            st.stop()
        if col3.button("Reagendar", key="rea" + patients_name):
            pass
        if col4.button("No se realizó", key="falta" + patients_name):
            with st.form(key="cancel_appointment"):
                reason_cancellation = st.selectbox("Seleccione el motivo",options=("Ausentismo","Reagendamiento por el paciente", "Reagendamiento por el tratante"))
                submit = st.form_submit_button("Guardar", type="primary")
            if submit:
                print("update appointment")
                # TODO update_appointment(reason=reason_cancellation)
        if col5.button("Cancelar", key="can" + patients_name):
            with st.form(key="cancel_appointment"):
                reason_cancellation = st.text_input("Razón para cancelar la cita")
                submit = st.form_submit_button("Cancelar", type="primary")
            if submit:
                print("update appointment")
                # TODO update_appointment(reason=reason_cancellation)

else:
    clean("Bienvenido al sistema de gestión de historias clínicas")

    login_info = login(
        client_id="418217949250-26re6hs241ls4v3eu3l73i433v53v6mo.apps.googleusercontent.com",
        client_secret="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",
        redirect_uri="http://localhost:8501",
        login_button_text="Iniciar sesión",
        logout_button_text="Logout",
    )

    practitioners = get_practitioner(st.session_state.db_engine)
    first_elements_list = [t.email for t in practitioners]
    if login_info and str(login_info[1]) in first_elements_list:
        st.session_state.logged_in = True
        practitioner_id = get_practitioner_by_email(st.session_state.db_engine, login_info[1])
        st.session_state.practitioner_login_id = practitioner_id[0]
        print(practitioner_id[0])
        st.experimental_rerun()
