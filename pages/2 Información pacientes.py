import datetime
import time
from datetime import datetime
import streamlit as st
import pandas as pd
from streamlit_extras.colored_header import colored_header
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from streamlit_extras.switch_page_button import switch_page
from data.actions.encounter_actions import (
    add_encounter,
    get_encounter_history,
    get_encounter,
    update_encounter,
    get_diagnostics,
    update_encounter_diagnostics,
)

from data.actions.patient_actions import get_patient_search, get_patient
from data.actions.questionnaire_actions import get_questionnaires
from data.actions.questionnaire_response_actions import (
    get_pending_questionnaire_responses,
    add_questionnaire_response,
    get_questionnaire_results,
    get_questionnaire_answers,
)
from data.conection import create_engine_conection
from data.create_database import Encounter

from utilidades.lists import list_encounter_types
from utilidades.vies_utilities import show_header, clean

if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine_conection()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

if "current_view" not in st.session_state:
    st.session_state.current_view = "Busqueda"

if "patient_id" not in st.session_state:
    st.session_state.patient_id = " "

if "register_encounter_page" not in st.session_state:
    st.session_state.register_encounter_page = " "

if "encounter_row_selected" not in st.session_state:
    st.session_state.encounter_row_selected = " "

if "previous_page" not in st.session_state:
    st.session_state.previous_page = ""


header_container = st.empty()
main_patient_info_view = st.empty()
with st.sidebar:
    controls_container = st.empty()
    encounters_container = st.empty()


# def displayPDF(file):
#     # Opening file from file path. this is used to open the file from a website rather than local
#     with urllib.request.urlopen(file) as f:
#         base64_pdf = base64.b64encode(f.read()).decode("utf-8")
#
#     # Embedding PDF in HTML
#     pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="950" type="application/pdf"></iframe>'
#
#     # Displaying File
#     st.markdown(pdf_display, unsafe_allow_html=True)


def inicio():
    if st.session_state.previous_page == "inicio":
        st.session_state.current_view = "inicio"
        st.session_state.encounter_row_selected = " "
        st.session_state.submit_cita = False

    else:
        if st.session_state.previous_page == "Busqueda":
            st.session_state.current_view = "Busqueda"
            st.session_state.encounter_row_selected = " "
            st.session_state.submit_cita = False
    # st.session_state.current_view = "Busqueda"


def atras():
    st.session_state.current_view = "Paciente"


def cambiar_pagina_historial(patient_id):
    st.session_state.patient_id = patient_id
    st.session_state.current_view = "Historial"


def cambiar_pagina_cita():
    st.session_state.current_view = "Nueva cita"


def cambiar_pagina_paciente(patient_id):
    st.session_state.patient_id = patient_id
    st.session_state.current_view = "Paciente"


def tab_registrar():
    st.session_state.register_encounter_page = True


def cambiar_pagina_editar():
    st.session_state.current_view = "Editar datos"


def show_encounter_history_view(id_to_search, encounter_row_selected=None):

    patient = get_patient(
        st.session_state.db_engine, id_to_search
    )  # Returns  object type Patient() to facilitate accessing patients data

    encounter_history_list = get_encounter_history(
        st.session_state.db_engine, patient.id
    )


    df_encounter_list = pd.DataFrame(
        encounter_history_list, columns=["Fecha", "Tipo de atención"], index=None
    ).astype(str) # astype because dataframes datatypes have issues being cast to be rendered
    df_encounter_list["Tipo de atención"].fillna("", inplace=True)

    builder = GridOptionsBuilder.from_dataframe(df_encounter_list)
    builder.configure_column(
        "Fecha", type=["customDateTimeFormat"], custom_format_string="yyyy-MM-dd"
    )
    builder.configure_selection(selection_mode="multiple", use_checkbox=False)
    builder.configure_side_bar(filters_panel=False)

    if st.session_state.encounter_row_selected != " ":
        builder.configure_selection(pre_selected_rows=[0])
    gridoptions = builder.build()

    with controls_container.container():
        colored_header(label="Controles", color_name="red-50", description="")
        st.button(
            "🏠 Regresar",
            type="primary",
            key="dos",
            on_click=inicio,
        )
        st.button("Registrar nueva sesión", on_click=tab_registrar)
        edit_encounter = st.button("Editar datos de la sesión")
        st.button("Recargar")

    with st.sidebar:
        colored_header(
            label="Historial de atención", color_name="red-50", description=""
        )

        st.write("Seleccione la sesión que desea visualizar")

        encounter_history_table = AgGrid(
            df_encounter_list,
            gridOptions=gridoptions,
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=False,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
        )

    encounter_row_selected = encounter_history_table["selected_rows"]

    if (
        st.session_state.register_encounter_page == True
    ):  # Compares if user wants to register an encounter and shows it's view
        st.header("Registrar nueva cita")
        register_encounter_container = st.empty()
        show_register_encounter_view(register_encounter_container)

    st.subheader(  # Apprears in all encounter's tabs
        "_Paciente: {0} {1} {2} {3}_".format(
            patient.first_name,
            patient.second_name,
            patient.first_family_name,
            patient.second_family_name,
        )
    )

    if encounter_row_selected:
        # Converts date formats here because the query has issues transforming dates
        date_from_selected_encounter = encounter_row_selected[0]["Fecha"]
        encounter_selected, practitioner_name = get_encounter(
            st.session_state.db_engine, patient.id, date_from_selected_encounter
        )

        if edit_encounter:  # TODO add update connection
            controls_container.empty()
            with controls_container.container():
                colored_header(label="Controles", color_name="red-50", description="")
                cancelado = st.button(
                    "❌ Cancelar edición",
                    type="primary",
                    on_click=change_view_encounter_history_no_id_with_rerun,
                )
                st.write("")
                st.write("")
            placeholder = st.form(key="cita")
            with placeholder:
                fecha = st.date_input(
                    "Fecha de cita",
                    value=datetime.strptime(date_from_selected_encounter, "%Y-%m-%d"),
                )
                encargado = st.text_input("Tratante", value="Juan Perez")
                descripcion = st.selectbox(
                    "Tipo de atención",
                    list_encounter_types,
                    help="Puede escribir aquí para buscar un tipo de atención",
                )
                asistencia = st.text_area(
                    "Información pertinente a la atención",
                    value=encounter_selected.topics_boarded,
                )

                tareas = st.text_input("Tareas enviadas", value="Lorem ipsum")
                archivos = st.file_uploader("Adjuntar archivos:")
                guardar = st.form_submit_button(label="Guardar")

        else:
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
                st.experimental_data_editor(df_encounter_list, use_container_width=True)

            with cuestionarios:
                questionnaires = get_questionnaires(st.session_state.db_engine)
                dict_questionnaires = {}
                for questionnaire in questionnaires:
                    dict_questionnaires[questionnaire.name] = questionnaire.id
                with st.form(key="questionnaires"):
                    questionnaires_selected = st.multiselect(
                        "Seleccione los cuestionarios/escalas/inventarios que desa asignar al paciente",
                        dict_questionnaires.keys()
                    )
                    if st.form_submit_button("Guardar"):
                        for questionnaire in questionnaires_selected:
                            add_questionnaire_response(
                                st.session_state.db_engine,
                                date_from_selected_encounter,
                                patient.id,
                                dict_questionnaires.get(questionnaire),
                            )

                quest = get_pending_questionnaire_responses(
                    st.session_state.db_engine, date_from_selected_encounter, patient.id
                )
                answers = get_questionnaire_results(
                    st.session_state.db_engine, date_from_selected_encounter, patient.id
                )

                if len(quest) > 0:
                    st.caption("Cuestionarios pendientes")
                    st.dataframe(quest)

                if len(answers) > 0:
                    st.markdown("##### Cuestionarios resueltos")
                    builder = GridOptionsBuilder.from_dataframe(answers)
                    builder.configure_selection(
                        selection_mode="single", use_checkbox=True
                    )
                    gridoptions = builder.build()

                    questionnaire_response_select = AgGrid(
                        answers,
                        gridOptions=gridoptions,
                        fit_columns_on_grid_load=True,
                        enable_enterprise_modules=False,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                    )

                    if len(questionnaire_response_select.selected_rows) > 0:
                        a = get_questionnaire_answers(
                            st.session_state.db_engine,
                            encounter_selected.date,
                            st.session_state.patient_id
                        )
                        st.download_button("Descargar respuestas", a.to_string())

            with archivos_adjuntos:
                st.markdown("#### Cargar archivos")
                with st.form(key="upload_file", clear_on_submit=True):
                    uploaded_files = st.file_uploader(
                        "Subir nuevos archivos adjuntos", accept_multiple_files=True
                    )
                    submit = st.form_submit_button("Guardar archivos")
                if submit:
                    for uploaded_file in uploaded_files:
                        bytes_data = uploaded_file.read()
                        path = r"bin/" + uploaded_file.name
                        with open(path, "wb") as binary_file:
                            # Write bytes to file
                            binary_file.write(bytes_data)
                st.markdown("#### Descargar archivos guardados")

                st.download_button("Archivo 1", data="Archivo de prueba")
                st.download_button("Archivo 2", data="Archivo de prueba")

            with diagnosticos:  # TODO add diagnostic list to encounter table
                diagnostics_list = get_diagnostics(
                    st.session_state.db_engine,
                    st.session_state.patient_id,
                    encounter_selected.date,
                )
                with st.form(key="new_diagnostic", clear_on_submit=False):
                    st.markdown(
                        "###### Agrege o elimine diagnósticos a la tabla y presione guardar"
                    )
                    result = st.experimental_data_editor(
                        diagnostics_list, num_rows="dynamic", use_container_width=True
                    )
                    submit = st.form_submit_button("Guardar")
                if submit:
                    update_encounter_diagnostics(
                        st.session_state.db_engine,
                        date=encounter_selected.date,
                        patient_id=st.session_state.patient_id,
                        diagnostics=result["Diagnósticos"],
                    )
                    st.success("Diágnosticos guardados con éxito")
                    time.sleep(0.5)
                    st.experimental_rerun()

    colored_header(label="Datos personales", color_name="red-50", description="")
    with st.expander("**Datos personales**"):
        dataframe_inicial = [
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
        personal_information_container = st.empty()
        edit_personal_info = st.button("Editar", key="editar_datos")

        if edit_personal_info:
            # TODO add edit personal info view
            print("Hi")
        else:
            with personal_information_container:
                df_encounter_list = pd.DataFrame(
                    dataframe_inicial, columns=["Campo", "Valor"]
                ).astype(
                    str
                )  # astype because dataframes datatypes have issues being cast to be rendered

                builder = GridOptionsBuilder.from_dataframe(df_encounter_list)
                gridoptions = (
                    builder.build()
                )  # TODO clean this code, choose aggrid or table
                # AgGrid(tabla, gridOptions=gridoptions, fit_columns_on_grid_load=True, enable_enterprise_modules=False)
                st.table(df_encounter_list)
    with st.expander("**Antecedentes**"):
        st.write("**Personales:** ", patient.personal_history)
        st.write("**Familiares:**", patient.family_history)
        st.button("Editar", key="editar_personales")
    with st.expander("**Información adicional**"):
        st.write(patient.extra_information)
        st.button("Editar", key="editar_adicional")


def change_view_encounter_history_no_id_with_rerun():
    st.session_state.current_view = "Historial"
    st.session_state.register_encounter_page = False
    st.experimental_rerun()


def change_view_encounter_history_no_id():
    st.session_state.current_view = "Historial"
    st.session_state.register_encounter_page = False


def show_successful_encounter_register():
    st.session_state.current_view = "encounter_success"
    st.session_state.register_encounter_page = False
    st.experimental_rerun()


def show_register_encounter_view(register_encounter_container):
    with register_encounter_container:
        controls_container.empty()
        with controls_container.container():
            colored_header(label="Controles", color_name="red-50", description="")

            cancelado = st.button(
                "❌ Cancelar registro",
                type="primary",
                on_click=change_view_encounter_history_no_id_with_rerun,
            )
            st.write("")
            st.write("")

        placeholder = st.form(key="cita", clear_on_submit=True)
        with placeholder:
            encounter = (
                Encounter()
            )  # Create Encounter object and then declares its fields as streamlit widgets directly | reduces calls and declarations
            encounter.date = st.date_input("Fecha de cita")

            encounter.encounter_type = st.selectbox(
                "Tipo de atención",
                list_encounter_types,
                help="Puede escribir aquí para buscar un tipo de atención",
            )
            encounter.topics_boarded = st.text_area(
                "Indique qué se abordó en la sesión:"
            )
            encounter.activities_sent = st.text_area(
                "Tareas/actividades a realizar para la proxima sesión"
            )
            encounter.attachments = st.file_uploader(
                "Busque o arrastre archivos a subir"
            )
            encounter.patient_id = st.session_state.patient_id
            encounter.practitioner_id = st.session_state.practitioner_login_id
            encounter.diagnostics = ""
            submit = st.form_submit_button("Guardar")

    if submit:
        add_encounter(st.session_state.db_engine, encounter)
        with register_encounter_container.empty():
            st.success(
                "La sesión fue grabada con éxito"
            )  # sleep because st.success needs time to be read by the user to move fordward
            time.sleep(1)
        change_view_encounter_history_no_id_with_rerun()


show_header(header_container)

if (
    st.session_state.current_view == "Busqueda"
):  # TODO Change patient search to also direct to the user individual report
    main_patient_info_view.empty()
    time.sleep(0.001)
    show_results = False

    previous_search_value = ""
    with main_patient_info_view.container():
        search_value = st.text_input("Ingrese la cédula o el apellido del paciente:")
    if (
        previous_search_value != search_value
    ):  # To avoid patient search running again if text typed by the user hasn't changed
        previous_search_value = search_value
        patient_search_results = get_patient_search(
            st.session_state.db_engine, search_value
        )

        if len(patient_search_results) == 0:
            st.warning("No existen resultados. ¿Deseas registrar un nuevo paciente?")
            if st.button("Registrar nuevo paciente", type="primary"):
                switch_page("Registrar_pacientes")
        else:
            st.markdown("##### Seleccione el paciente a visualizar")
            col1, col2 = st.columns([4, 1])
            df_patient_search_results = pd.DataFrame(
                patient_search_results,
                columns=[
                    "Cédula",
                    "Nombre1",
                    "Nombre2",
                    "Apellido1",
                    "Apellido2",
                    "Facultad/Dependencia",
                ],
                index=None,
            ).astype(str)
            df_patient_search_results["Nombre"] = df_patient_search_results[
                ["Nombre1", "Nombre2", "Apellido1", "Apellido2"]
            ].apply(" ".join, axis=1)
            df_patient_search_results = df_patient_search_results[
                ["Cédula", "Nombre", "Facultad/Dependencia"]
            ]
            builder = GridOptionsBuilder.from_dataframe(df_patient_search_results)
            builder.configure_selection(selection_mode="single", use_checkbox=False)
            builder.configure_side_bar(filters_panel=False)
            gridoptions = builder.build()
            with col1:
                if st.session_state.current_view != "Historial":
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
                st.session_state.current_view = "Historial"
                st.session_state.patient_id = selected_patient[0]["Cédula"]
                st.session_state.previous_page = "Busqueda"
                st.experimental_rerun()

            if col2.button("Generar reporte"):
                st.session_state.current_view = "generate_report"
                st.write("Reporte")
                st.experimental_rerun()


if st.session_state.current_view == "Historial":
    main_patient_info_view.empty()
    with st.container():
        show_encounter_history_view(st.session_state.patient_id)

if st.session_state.current_view == "inicio":
    st.session_state.current_view = "Busqueda"
    switch_page("inicio")
