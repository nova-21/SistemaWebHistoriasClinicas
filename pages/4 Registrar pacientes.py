import datetime
import time
from time import sleep

import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, ColumnsAutoSizeMode, AgGrid

from data.actions.patient_actions import add_patient
from data.actions.practitioner_actions import add_practitioner, get_practitioner, delete_practitioner
from data.conection import create_engine_conection
from data.create_database import Patient, Practitioner
from utilidades.lists import tipos_de_paciente
from utilidades.vies_utilities import clean, load_logo

load_logo()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine_conection()

if st.session_state.user_info == {}:
    clean("Por favor inicie sesión para continuar")

if "delete_practitioner_flag" not in st.session_state:
    st.session_state.delete_practitioner_flag = False



def register_practicioner():
    practitioner = Practitioner()

    with st.form("register_practitioner", clear_on_submit=True):
        practitioner.id = st.text_input(
            "Cédula*",
            help="Cualquier documento de identificación es permitido en caso de personas extranjeras",
        )
        practitioner.full_name=st.text_input("Nombre completo")
        practitioner.email = st.text_input("Email")
        practitioner.position = st.selectbox("Posición",("Psicólogo clínico", "Psicóloco educativo", "Psiquiatra", "Administrador"))
        practitioner.phone_number = st.text_input("Teléfono")
        submit_practitioner=st.form_submit_button("Guardar")

    if submit_practitioner:
        add_practitioner(st.session_state.db_engine, practitioner.id, practitioner.full_name, practitioner.position, practitioner.email, practitioner.phone_number, True)
        st.success("Tratante guardado con éxito")
        time.sleep(2)
        st.experimental_rerun()

def remove_practitioner():
    practitioners_list = get_practitioner(st.session_state.db_engine)
    practitioners_history = pd.DataFrame(practitioners_list, columns=['email', 'id'])
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

    sesion = AgGrid(
        practitioners_history,
        gridOptions=gridoptions,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
        enable_enterprise_modules=False,
    )

    practitioner_selected = sesion["selected_rows"]

    if st.button("Dar de baja al tratante") and practitioner_selected != []:
        st.session_state.delete_practitioner_flag = True

    if st.session_state.delete_practitioner_flag == True:
        st.warning("¿Está seguro? Este cambio no puede ser revertido")
        col1,col2 = st.columns(2)

        if st.button("Si, dar de baja"):
            st.error("El tratante ha sido dado de baja")
            delete_practitioner(st.session_state.db_engine,practitioner_selected[0]["id"])
            time.sleep(2)
            st.session_state.delete_practitioner_flag = False
            st.experimental_rerun()

        if st.button("No, cancelar"):
            st.session_state.delete_practitioner_flag = False
            st.experimental_rerun()

def registrar_paciente(base):
    with base:
        patient = Patient()

        with st.form("registro", clear_on_submit=False):
            patient.id = st.text_input(
                "Cédula/Pasaporte*",
                help="Pasaporte en caso de personas extranjeras",
            )
            patient.first_name = st.text_input("Primer nombre*")
            patient.second_name = st.text_input("Segundo nombre")
            patient.first_family_name = st.text_input("Primer apellido*")
            patient.second_family_name = st.text_input("Segundo apellido")
            patient.preferred_name = st.text_input("Nombre preferido", help="Puede o no ser uno de sus nombres legales")
            patient.birth_date = st.date_input(
                "Fecha de nacimiento (Año/Mes/Día)*",
                min_value=datetime.date(1900, 1, 1),
            )
            patient.sex = st.text_input("Sexo")
            patient.gender = st.text_input("Género")
            patient.sexual_orientation = st.text_input("Orientación sexual")
            patient.phone_number = st.text_input("Teléfono*")
            patient.email = st.text_input("E-mail*")
            patient.profession_occupation = st.text_input("Profesión/Ocupación")
            patient.maritalStatus = st.selectbox(
                "Estado civil*",
                ("Soltero", "Casado", "Divorciado", "Viudo", "Union de hecho"),
            )
            patient.patient_type = st.selectbox(
                "Tipo de paciente*", options=tipos_de_paciente
            )
            patient.faculty_dependence = st.text_input(
                "Facultad/Dependencia*",
                help="Facultad para estudiantes, docentes, personal administrativo. Dependencia para otros trabajaores.",
            )
            patient.career = st.text_input(
                "Carrera", help="Unicamente en caso de ser estudiante u egresado"
            )
            patient.semester = st.text_input(
                "Ciclo",
                help="Actualizar cada semestre, dejar en blanco si es egresado",
            )
            patient.city_born = st.text_input("Ciudad de nacimiento")
            patient.city_residence = st.text_input("Ciudad de residencia")
            patient.address = st.text_input("Dirección del domicilio")
            patient.children = st.number_input("Número de hijos", min_value=0)
            patient.lives_with = st.text_input(
                "Personas con las que vive",
                placeholder="Ingrese las personas separadas con una coma.",
            )
            patient.emergency_contact_name = st.text_input(
                "Nombre del contacto de emergencia*"
            )
            patient.emergency_contact_relation = st.text_input(
                "Relación del contacto de emergencia*",
                help="Por ejemplo: Padre, Madre, Hermano",
            )
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
            submit = st.form_submit_button("Registrar")
        if submit:
            try:
                if patient.id == "":
                    raise ValueError(
                        "El campo cédula o identificación es obligatorio."
                    )
                if patient.first_name == "":
                    raise ValueError("El campo primer nombre es obligatorio.")
                if patient.first_family_name == "":
                    raise ValueError("El campo primer apellido es obligatorio.")
                if patient.birth_date == "":
                    raise ValueError("El campo fecha de nacimiento es obligatorio.")
                if patient.maritalStatus == "":
                    raise ValueError("El campo fecha de nacimiento es obligatorio.")
                if patient.patient_type == "":
                    raise ValueError("El campo fecha de nacimiento es obligatorio.")
                if patient.emergency_contact_name == "":
                    raise ValueError("El campo fecha de nacimiento es obligatorio.")
                if patient.emergency_contact_relation == "":
                    raise ValueError("El campo fecha de nacimiento es obligatorio.")
                if patient.emergency_contact_phone == "":
                    raise ValueError("El campo fecha de nacimiento es obligatorio.")

                # TODO add already registered control
                message_result = add_patient(
                    db_engine=st.session_state.db_engine, patient=patient
                )
                return message_result
            except:
                st.error(
                    "Uno o más campos obligatorios se encuentran vacíos, por favor revise los datos y vuelva a guardar."
                )
                sleep(4)
                st.experimental_rerun()

if st.session_state.user_info:

    clean(
        "Registro de pacientes",
        "Ingrese los datos personales del paciente a registrar, los campos con asteriscos (*) son obligatorios",
    )

    if st.session_state.user_info.get("email") == "alex.pinos@ucuenca.edu.ec":
        tab1, tab2, tab3 = st.tabs(["Pacientes", "Tratantes", "Dar de baja tratante"])
        with tab1:
            base = st.empty()
            message_result = registrar_paciente(base)
        with tab2:
            register_practicioner()
        with tab3:
            remove_practitioner()
    else:
        base = st.empty()
        message_result = registrar_paciente(base)

    if message_result == "Paciente registrado con éxito":
        base.empty()
        st.success(message_result)
        st.button("Aceptar")
    if message_result == "El paciente ya se encuentra registrado":
        base.empty()
        st.error(message_result)
        st.button("Aceptar")
