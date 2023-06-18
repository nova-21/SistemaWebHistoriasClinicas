import datetime
import time
from time import sleep

import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, ColumnsAutoSizeMode, AgGrid

from data.repositories.PatientRepository import add_patient_object
from data.repositories.PractitionerRepository import add_practitioner, get_practitioners, delete_practitioner
from data.database_connection import create_engine_conection
from data.database_declaration import Patient, Practitioner
from utilities.lists import tipos_de_paciente, facultades, posiciones_tratantes
from utilities.session_state_utilities import get_or_create_session_state
from utilities.view_utilities import clean, load_logo

load_logo()

def register_practicioner(base_practitioner):
    """
        Registers a practitioner.

        Args:
            base_practitioner: The base container practitioner.

        """
    with base_practitioner:
        practitioner = Practitioner()

        with st.form("register_practitioner", clear_on_submit=False):
            st.write("#### Registro de tratantes")
            st.write(
                "##### Ingrese los datos personales y presione Registrar. Los campos con asterisco (*) son obligatorios")
            practitioner.id = st.text_input(
                "Cédula*",
                help="Cualquier documento de identificación es permitido en caso de personas extranjeras",
                value=get_or_create_session_state("practitioner_id", "")
            )
            practitioner.full_name = st.text_input("Nombre completo*",
                                                   value=get_or_create_session_state("practitioner_full_name",
                                                                                     "")).lower().title()
            practitioner.email = st.text_input("Email*", value=get_or_create_session_state("practitioner_email", ""))
            practitioner.position = st.selectbox("Posición*", posiciones_tratantes,
                                                 index=get_or_create_session_state("practitioner_position_index", 0))
            practitioner.phone_number = st.text_input("Teléfono*",
                                                      value=get_or_create_session_state("practitioner_phone_number",
                                                                                        ""))
            submit_practitioner = st.form_submit_button("Registrar", type="primary")

        if submit_practitioner:
            try:
                if practitioner.full_name == "":
                    raise ValueError("El campo Nombre completo es obligatorio.")
                if practitioner.email == "":
                    raise ValueError("El campo email es obligatorio.")
                if practitioner.position == "":
                    raise ValueError("El campo Posición es obligatorio.")
                if practitioner.phone_number == "":
                    raise ValueError("El campo Teléfono es obligatorio.")

                add_practitioner(
                    st.session_state.db_engine,
                    practitioner.id,
                    practitioner.full_name,
                    practitioner.position,
                    practitioner.email,
                    practitioner.phone_number,
                    True
                )

                st.success("Tratante guardado con éxito")
                time.sleep(2)
                st.experimental_rerun()

            except ValueError as e:
                st.error(str(e))
                sleep(4)
                st.experimental_rerun()

            except Exception:
                st.error(
                    "Uno o más campos obligatorios se encuentran vacíos, por favor revise los datos y vuelva a guardar.")
                sleep(4)
                st.experimental_rerun()

def remove_practitioner():
    """
        Disables access to practitioner in the system

        """
    practitioners_list = get_practitioners(st.session_state.db_engine)
    practitioners_history = pd.DataFrame(practitioners_list, columns=['full_name', 'email', 'id', 'position'])
    if len(practitioners_list) == 0:
        st.success("No tiene citas pendientes el día de hoy")

    builder = GridOptionsBuilder.from_dataframe(practitioners_history)
    builder.configure_selection(selection_mode="single", use_checkbox=False)
    builder.configure_default_column(
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW
    )
    other_options = {"suppressColumnVirtualisation": True}
    builder.configure_grid_options(**other_options)
    gridoptions = builder.build()
    st.write("**Seleccione un tratante para dar de baja.**")
    st.write("**El tratante ya no tendrá acceso al sistema, pero sus datos se mantendrán en el sistema.**")
    sesion = AgGrid(
        practitioners_history,
        gridOptions=gridoptions,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
        enable_enterprise_modules=False,
    )

    practitioner_selected = sesion["selected_rows"]

    if st.button("Dar de baja al tratante", type="primary") and practitioner_selected != []:
        get_or_create_session_state("delete_practitioner_flag", True)

    if get_or_create_session_state("delete_practitioner_flag", False) == True:
        st.warning("¿Está seguro? Este cambio no puede ser revertido")
        col1, col2 = st.columns([0.3, 3])
        if col1.button("Si, dar de baja"):
            st.error("El tratante ha sido dado de baja")
            delete_practitioner(st.session_state.db_engine, practitioner_selected[0]["id"])
            time.sleep(2)
            get_or_create_session_state("delete_practitioner_flag", False)
            st.experimental_rerun()

        if col2.button("No, cancelar"):
            get_or_create_session_state("delete_practitioner_flag", False)
            st.experimental_rerun()


def registrar_paciente(base):
    """
        Creates a patient registration form and handles the submission.

        Args:
            base: The base Streamlit element to display the form.
            db_engine: The database engine connection.

        Returns:
            str: A message indicating the status of the patient registration.
        """

    with base:

        patient = Patient()

        with st.form("registro", clear_on_submit=False):
            st.write("#### Registro de pacientes")
            st.write(
                "##### Ingrese los datos personales y presione Registrar, los campos con asteriscos (*) son obligatorios",
            )
            st.write("###### Recuérdele al paciente que está en su derecho a rehusarse a otorgar datos no escenciales para el registro")
            patient.id = st.text_input(
                "Cédula/Pasaporte*",
                help="Pasaporte en caso de personas extranjeras",
            )
            patient.first_name = st.text_input("Primer nombre*").capitalize()
            patient.second_name = st.text_input("Segundo nombre").capitalize()
            patient.first_family_name = st.text_input("Primer apellido*").capitalize()
            patient.second_family_name = st.text_input("Segundo apellido").capitalize()
            patient.preferred_name = st.text_input("Nombre preferido", help="Puede o no ser uno de sus nombres legales, apodo.").capitalize()
            patient.birth_date = st.date_input(
                "Fecha de nacimiento (Año/Mes/Día)*",
                min_value=datetime.date(1900, 1, 1),
            )
            patient.sex = st.text_input("Sexo").capitalize()
            patient.gender = st.text_input("Género").capitalize()
            patient.sexual_orientation = st.text_input("Orientación sexual").capitalize()
            patient.phone_number = st.text_input("Teléfono*")
            patient.email = st.text_input("E-mail*")
            patient.profession_occupation = st.text_input("Profesión/Ocupación").capitalize()
            patient.maritalStatus = st.selectbox(
                "Estado civil",
                ("Soltero", "Casado", "Divorciado", "Viudo", "Union de hecho", "Prefiere no decir"),
            )
            patient.patient_type = st.selectbox(
                "Tipo de paciente*", options=tipos_de_paciente
            )

            patient.faculty = st.selectbox(
                "Facultad (Solo para Estudiante, Egresado y Docente)", options=facultades, index=0,
                help="Seleccione Ninguna si no pertenece a estos grupos.",
            )
            patient.dependence = st.text_input(
                "Dependencia (Solo para Trabajador, Jubilado y Familiar)",
                help="Personal administrativo, biblioteca, investigación, etc. Dejar en blanco si no pertenece a estos grupos",
            )
            if patient.faculty == "Ninguna":
                patient.faculty_dependence = patient.dependence
            else:
                patient.faculty_dependence = patient.faculty
            patient.career = st.text_input(
                "Carrera", help="Unicamente en caso de ser estudiante u egresado"
            ).capitalize()
            patient.semester = st.text_input(
                "Ciclo, en números (Solo para pacientes de tipo Estudiante)",
                help="Dejar en blanco para egresados, docentes, etc.",
            )
            patient.city_born = st.text_input("Ciudad de nacimiento").capitalize()
            patient.city_residence = st.text_input("Ciudad de residencia").capitalize()
            patient.address = st.text_input("Dirección del domicilio")
            patient.children = st.number_input("Número de hijos", min_value=0)
            patient.lives_with = st.text_input(
                "Personas con las que vive",
                placeholder="Ingrese las personas separadas con una coma.",
            )
            patient.emergency_contact_name = st.text_input(
                "Nombre del contacto de emergencia*"
            ).lower().title()
            patient.emergency_contact_relation = st.text_input(
                "Relación del contacto de emergencia*",
                help="Por ejemplo: Padre, Madre, Hermano",
            ).capitalize()
            patient.emergency_contact_phone = st.text_input(
                "Teléfono del contacto de emergencia*"
            )
            patient.family_history = st.text_area(
                "Antecedentes patológicos familiares",
            )
            patient.personal_history = st.text_area(
                "Antecedentes patológicos personales",
            )
            patient.habits = st.text_area(
                "Hábitos",
                help="tabaquismo, alcoholismo, drogas, etc.",
            )
            patient.extra_information = st.text_area(
                "Información adicional",
                help="Espacio para cualquier otro tipo de información",
            )
            patient.active = True
            submit = st.form_submit_button("Registrar", type="primary")
        if submit:
            try:
                if patient.id == "":
                    raise ValueError(
                        "El campo cédula o identificación es obligatorio."
                    )
                if patient.first_name == "":
                    raise ValueError("El campo Primer nombre es obligatorio.")
                if patient.first_family_name == "":
                    raise ValueError("El campo Primer apellido es obligatorio.")
                if patient.birth_date == "":
                    raise ValueError("El campo Fecha de nacimiento es obligatorio.")
                if patient.patient_type == "":
                    raise ValueError("El campo Tipo de paciente obligatorio.")
                if patient.emergency_contact_name == "":
                    raise ValueError("El campo Contacto de emergencia es obligatorio.")
                if patient.emergency_contact_relation == "":
                    raise ValueError("El campo Relación del contacto de emergencia es obligatorio.")
                if patient.emergency_contact_phone == "":
                    raise ValueError("El campo Teléfono de contacto de emergencia es obligatorio.")

                # TODO add already registered control
                message_result = add_patient_object(
                    db_engine=st.session_state.db_engine, patient=patient
                )
                return message_result
            except Exception as e:
                st.error(
                    e.args[0]
                )
                sleep(4)
                st.experimental_rerun()



logged_in = get_or_create_session_state("logged_in", True)
db_engine = get_or_create_session_state("db_engine", create_engine_conection())
user_info = get_or_create_session_state("user_info", {})
base_patient = st.empty()

# Check if user is logged in
if st.session_state.user_info:
    clean("Registro de pacientes y tratantes")

    # Check if the user is an administrator
    if st.session_state.practitioner_position == "Administrator":
        # Create tabs for Patients, Practitioners, and Removing Practitioners
        tab1, tab2, tab3 = st.tabs(["Pacientes", "Tratantes", "Dar de baja tratante"])

        # Handle registration of patients
        with tab1:
            base_patient = st.empty()
            message_result = registrar_paciente(base_patient)

        # Handle registration of practitioners
        with tab2:
            base_practitioner = st.empty()
            register_practicioner(base_practitioner)

        # Handle removal of practitioners
        with tab3:
            base_rem_practitioner = st.empty()
            remove_practitioner()

    # If the user is not an administrator, only handle patient registration
    else:
        base = st.empty()
        message_result = registrar_paciente(base)

    # Display success message and accept button if patient registration is successful
    if message_result == "Paciente registrado con éxito":
        base_patient.empty()
        st.success(message_result)
        st.button("Aceptar")

    # Display error message and accept button if patient is already registered
    if message_result == "El paciente ya se encuentra registrado":
        base_patient.empty()
        st.error(message_result)
        st.button("Aceptar")
