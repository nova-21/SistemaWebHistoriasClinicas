import os
from sqlalchemy import create_engine
from st_aggrid import GridOptionsBuilder, AgGrid
from streamlit_extras.switch_page_button import switch_page
from data.actions.appointment_actions import get_todays_appointments, update_appointment
from data.actions.practitioner_actions import get_practitioner, get_practitioner_by_email
from data.conection import create_engine_conection
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



#
# with st.sidebar:
#     # login_info = login(
#     #     client_id=st.secrets["client_id"],
#     #     client_secret=st.secrets["client_secret"],
#     #     redirect_uri=st.secrets["redirect_uri"],
#     #     login_button_text=st.secrets["login_button_text"],
#     #     logout_button_text=st.secrets["logout_button_text"],
#     # )
#     login_info = login(
#         client_id=st.secrets["client_id"],
#         client_secret=st.secrets["client_secret"],
#         redirect_uri=st.secrets["redirect_uri"],
#         login_button_text=st.secrets["login_button_text"],
#         logout_button_text=st.secrets["logout_button_text"],
#     )
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


