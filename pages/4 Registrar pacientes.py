import datetime
import os
from time import sleep

import streamlit as st
from sqlalchemy import create_engine

from data.actions.patient_actions import add_patient
from data.conection import create_engine_conection
from data.create_database import Patient
from utilidades.lists import tipos_de_paciente
from utilidades.vies_utilities import clean, load_logo

load_logo()
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine_conection()


def registrar_paciente(base):
    with base:
        patient = Patient()

        with st.form("registro", clear_on_submit=False):
            patient.id = st.text_input(
                "Cédula*",
                help="Cualquier documento de identificación es permitido en caso de personas extranjeras",
            )
            patient.first_name = st.text_input("Primer nombre*")
            patient.second_name = st.text_input("Segundo nombre")
            patient.first_family_name = st.text_input("Primer apellido*")
            patient.second_family_name = st.text_input("Segundo apellido")
            patient.preferred_name = st.text_input("Nombre preferido")
            patient.birth_date = st.date_input(
                "Fecha de nacimiento (Año/Mes/Día)*", min_value=datetime.date(1900, 1, 1)
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
                "Ciclo", help="Actualizar cada semestre, dejar en blanco si es egresado"
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
                "Antecedentes familiares",
                help="Ejemplo: Información clínica pertinente, relaciones personales con familiares.",
            )
            patient.personal_history = st.text_area(
                "Antecedentes personales",
                help="Información clínica relevante del patiente",
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
                    raise ValueError("El campo cédula o identificación es obligatorio.")
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

                # TODO add validations and already registered control
                # patient = Patient(id=id, first_name=first_name, second_name=second_name,
                #                   first_family_name=first_family_name, second_family_name=second_family_name,
                #                   preferred_name=preferred_name, birth_date=birth_date,
                #                   sex=sex,
                #                   gender=gender,
                #                   sexual_orientation=sexual_orientation,
                #                   phone_number=phone_number,
                #                   email=email,
                #                   profession_occupation=profession_occupation,
                #                   marital_status=maritalStatus,
                #                   patient_type=patient_type,
                #                   faculty_dependence=faculty_dependence,
                #                   career=career,
                #                   semester=semester,
                #                   city_born=city_born,
                #                   city_residence=city_residence,
                #                   address=address,
                #                   children=children,
                #                   lives_with=lives_with,
                #                   emergency_contact_name=emergency_contact_name,
                #                   emergency_contact_relation=emergency_contact_relation,
                #                   emergency_contact_phone=emergency_contact_phone,
                #                   family_history=family_history,
                #                   personal_history=personal_history,
                #                   extra_information=extra_information,
                #                   active=active
                #                   )
                message_result = add_patient(
                    db_engine=st.session_state.db_engine, patient=patient
                )
                return message_result
            except:
                st.error("Uno o más campos obligatorios se encuentran vacíos, por favor revise los datos y vuelva a guardar.")
                sleep(4)
                st.experimental_rerun()


clean("Registro de pacientes", "Ingrese los datos personales del paciente a registrar, los campos con asteriscos (*) 0son obligatorios")


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
