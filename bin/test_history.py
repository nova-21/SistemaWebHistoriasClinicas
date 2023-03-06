import os
import time

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from st_aggrid import AgGrid, GridUpdateMode, GridOptionsBuilder
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page

from Inicio import gridoptions
from data.actions.encounter_actions import get_encounter_history, get_encounter
from data.actions.patient_actions import get_patient_search, get_patient
from utilidades.vies_utilities import show_header

if "current_view" not in st.session_state:
    st.session_state.current_view = "search_patient_view"

if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine(os.environ.get("DATABASE"))

if "patient_id" not in st.session_state:
    st.session_state.patient_id = ""

if "is_encounter_selected" not in st.session_state:
    st.session_state.is_encounter_selected = None

header_container = st.empty()
patient_history_view = st.empty()
main_patient_info_view = st.empty()

with st.sidebar:
    controls_container = st.empty()
    encounters_container = st.empty()


if st.session_state.current_view == "search_patient_view":
    main_patient_info_view.empty()
    previous_search_value = ""
    main_patient_info_view = st.container()

    with main_patient_info_view:

        search_value = st.text_input("Ingrese la cédula o los apellidos del paciente:")
    if (
            previous_search_value != search_value and search_value != ""
    ):  # To avoid patient search running again if text typed by the user hasn't changed
        previous_search_value = search_value
        patient_search_results = get_patient_search(
            st.session_state.db_engine, search_value
        )

        if len(patient_search_results) == 0:
            st.warning(
                "No existen resultados. ¿Deseas registrar un nuevo paciente?"
            )
            if st.button("Registrar nuevo paciente", type="primary"):
                switch_page("Registrar_pacientes")
        else:
            st.markdown("##### Seleccione el paciente a visualizar")
            col1, col2 = st.columns([4,1])
            with col1:
                df_patient_search_results = pd.DataFrame(
                    patient_search_results, columns=["Cédula", "Nombre1", "Nombre2", "Apellido1", "Apellido2", "Facultad/Dependencia"], index=None
                ).astype(str)
                df_patient_search_results["Nombre"] = df_patient_search_results[["Nombre1", "Nombre2", "Apellido1", "Apellido2"]].apply(" ".join,axis=1)
                df_patient_search_results = df_patient_search_results[["Cédula","Nombre","Facultad/Dependencia"]]
                builder = GridOptionsBuilder.from_dataframe(df_patient_search_results)
                builder.configure_selection(selection_mode="single", use_checkbox=False)
                builder.configure_side_bar(filters_panel=False)

                gridoptions = builder.build()
                patients_found = AgGrid(
                    df_patient_search_results,
                    gridOptions=gridoptions,
                    fit_columns_on_grid_load=True,
                    enable_enterprise_modules=False,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                )

                selected_patient = patients_found["selected_rows"]
            col2.write("")
            col2.write("")
            if col2.button("Ver paciente"):
                st.session_state.current_view = "profile_history_view"
                st.session_state.patient_id = selected_patient[0]["Cédula"]
                st.write(st.session_state.patient_id)
                st.experimental_rerun()
            if col2.button("Generar reporte"):
                st.session_state.current_view = "generate_report"
                st.write("Reporte")
                st.experimental_rerun()

if st.session_state.current_view == "profile_history_view":
    main_patient_info_view.empty()
    show_header(header_container)

    patient = get_patient(
        st.session_state.db_engine, st.session_state.patient_id
    )  # Returns  object type Patient() to facilitate accessing patients data

    personal_data = [
        ["Cédula", patient.id],
        ["Nombre preferido", patient.preferred_name],
        ["Sexo", patient.sex],
        ["Género", patient.gender],
        ["Orientación sexual", patient.sexual_orientation],
        ["Fecha de nacimiento", patient.birth_date],
        ["Teléfono", patient.phone_number],
        ["E-mail", patient.email],
        ["Ocupación", patient.profession_occupation],
        ["Estado civil", patient.marital_status],
        ["Rol universitario", patient.patient_type],
        ["Facultad/Dependencia", patient.faculty_dependence],
        ["Carrera", patient.career],
        ["Ciclo", patient.semester],
        ["Ciudad de nacimiento", patient.city_born],
        ["Ciudad de residencia", patient.city_residence],
        ["Dirección del domicilio", patient.address],
        ["Número de hijos", patient.children],
        ["Personas con las que vive", patient.lives_with],
        ["Nombre del contado de emergencia", patient.emergency_contact_name],
        ["Relación del contacto de emergencia", patient.emergency_contact_relation],
        ["Teléfono del contacto de emergencia", patient.emergency_contact_phone],
    ]

    df_personal_data = pd.DataFrame(
        personal_data, columns=["Campo", "Valor"]
    ).astype(
        str
    )  # astype because dataframes datatypes have issues being cast to be rendered

    encounter_history_list = get_encounter_history(
        st.session_state.db_engine, st.session_state.patient_id
    )

    # astype because dataframes datatypes have issues being cast to be rendered
    df_encounter_list = pd.DataFrame(
        encounter_history_list, columns=["Fecha", "Tipo de atención"], index=None
    ).astype(str)
    builder = GridOptionsBuilder.from_dataframe(df_encounter_list)
    builder.configure_column(
        "Fecha", type=["customDateTimeFormat"], custom_format_string="yyyy-MM-dd"
    )
    builder.configure_selection(selection_mode="multiple", use_checkbox=False)
    builder.configure_side_bar(filters_panel=False)
    gridoptions = builder.build()

    with controls_container.container():
        colored_header(label="Controles", color_name="red-50", description="")
        if st.button(
            "🏠 Regresar a la búsqueda de pacientes",
            type="primary",
            key="dos"
        ):
            if st.session_state.previous_page == "inicio":
                st.session_state.current_view = "inicio"

            else:
                if st.session_state.previous_page == "Busqueda":
                    st.session_state.current_view = "Busqueda"
        st.button("Registrar nueva sesión", on_click=1)
        edit_encounter = st.button("Editar datos de la sesión")
        colored_header(
            label="Historial de atención", color_name="red-50", description=""

        )
        st.write("Seleccione la sesión que desea visualizar")

    with st.sidebar:
        encounter_history_table = AgGrid(
            df_encounter_list,
            gridOptions=gridoptions,
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=False,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
        )

    with main_patient_info_view.container():
        st.subheader(  # Apprears in all encounter's tabs
            "_Paciente: {0} {1} {2} {3}_".format(
                patient.first_name,
                patient.second_name,
                patient.first_family_name,
                patient.second_family_name,
            )
        )
        colored_header(label="Información del paciente", color_name="red-50", description="")

        with st.expander("**Datos personales**"):
            st.table(df_personal_data)
        with st.expander("**Antecedentes**"):
            st.write("**Personales:** ",patient.personal_history)
            st.write("**Familiares:**",patient.family_history)
            st.button("Editar", key="editar_personales")
        with st.expander("**Información adicional**"):
            st.write(patient.extra_information)
            st.button("Editar", key="editar_adicional")





st.session_state.is_encounter_selected=True

if st.session_state.current_view == "profile_history_view" and st.session_state.is_encounter_selected == True:
    encounter_row_selected = encounter_history_table["selected_rows"]
    if encounter_row_selected:
        # Converts date formats here because the query has issues transforming dates
        date_from_selected_encounter = encounter_row_selected[0]["Fecha"]
        encounter_selected, practitioner_name = get_encounter(
            st.session_state.db_engine, patient.id, date_from_selected_encounter
        )
    with patient_history_view.container():
        colored_header(
            label="Información de la sesión", color_name="red-50", description=""
        )

        informacion, cuestionarios, archivos_adjuntos, diagnosticos = st.tabs(
            ["Información", "Cuestionarios", "Archivos adjuntos", "Diagnósticos"]
        )
        with informacion:
            dataframe_inicial = [
                ["Fecha", encounter_selected.date],
                ["Tratante", practitioner_name],
                ["Tipo de atención", encounter_selected.encounter_type],
                ["Asuntos tratados", encounter_selected.topics_boarded],
                ["Tareas enviadas", encounter_selected.activities_sent],
            ]

            # astype because dataframes datatypes have issues being cast to be rendered
            df_encounter_list = pd.DataFrame(
                dataframe_inicial, columns=["Campo", "Valor"]
            ).astype(str)

            st.table(df_encounter_list)

if st.session_state.current_view == "generate_report":
    st.download_button("Descargar reporte de sesiones")


if st.session_state.current_view == "inicio":
    st.session_state.current_view = "search_patient_view"
    switch_page("inicio")
