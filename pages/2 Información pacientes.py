import datetime
import os
import time
from datetime import datetime
import streamlit as st
import pandas as pd
from streamlit_extras.colored_header import colored_header
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, ColumnsAutoSizeMode, AgGridTheme
from streamlit_extras.switch_page_button import switch_page

from data.actions.diagnostic_action import get_diagnostics, add_diagnostic
from data.actions.encounter_actions import (
    add_encounter,
    get_encounter_history,
    get_encounter, update_attachment, get_attachments_list, update_encounter,
)

from data.actions.patient_actions import get_patient_search, get_patient, get_all_patients
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

if "edit_encounter" not in st.session_state:
    st.session_state.edit_encounter = False


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
        encounter_history_list, columns=["Tipo de atención","Fecha"], index=None
    ).astype(str) # astype because dataframes datatypes have issues being cast to be rendered
    df_encounter_list["Tipo de atención"].fillna("", inplace=True)

    builder = GridOptionsBuilder.from_dataframe(df_encounter_list)
    builder.configure_column(
        "Fecha", type=["customDateTimeFormat"], custom_format_string="yyyy-MM-dd"
    )
    #TODO fix this table view
    builder.configure_selection(selection_mode="multiple", use_checkbox=False)
    builder.configure_side_bar(filters_panel=False)
    other_options = {'suppressColumnVirtualisation': True}
    builder.configure_grid_options(**other_options)


    if st.session_state.encounter_row_selected != " ":
        builder.configure_selection(pre_selected_rows=[0])
    gridoptions = builder.build()

    with controls_container.container():
        colored_header(label="Opciones", color_name="red-50", description="")
        st.button(
            "🏠 Regresar",
            type="primary",
            key="dos",
            on_click=inicio,
        )
        # st.button("Registrar nueva sesión", on_click=tab_registrar)
        edit_encounter = st.button("Editar datos de la sesión")
        if edit_encounter:
            st.session_state.edit_encounter = True
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
            enable_quicksearch=True,
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
        )

    encounter_row_selected = encounter_history_table["selected_rows"]

    if (
        st.session_state.register_encounter_page == True
    ):  # Compares if user wants to register an encounter and shows it's view
        st.header("Registrar nueva cita")
        register_encounter_container = st.empty()
        show_register_encounter_view(register_encounter_container)

    st.subheader(  # Apprears in all encounter's tabs
        "Paciente: {0} {1} {2} {3}".format(
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

        if st.session_state.edit_encounter:  # TODO add update connection
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

                encounter_selected.date = st.date_input(
                    "Fecha de cita",
                    value=datetime.strptime(date_from_selected_encounter, "%Y-%m-%d"),
                )
                encounter_selected.practitioner_name = st.text_input("Tratante", value=practitioner_name)
                encounter_selected.encounter_type = st.selectbox(
                    "Tipo de atención",
                    list_encounter_types,
                    help="Puede escribir aquí para buscar un tipo de atención",
                )
                encounter_selected.topics_boarded = st.text_area(
                    "Evolución del paciente:",
                    value=encounter_selected.topics_boarded,
                )

                encounter_selected.activities_sent = st.text_input("Tareas enviadas", value=encounter_selected.activities_sent)
                guardar = st.form_submit_button(label="Guardar")

            if guardar:
                update_encounter(st.session_state.db_engine, encounter_selected)
                st.success("Se ha guardado los cambios")
                time.sleep(1)
                st.session_state.edit_encounter = False
                st.session_state.encounter_row_selected = 0
                st.experimental_rerun()



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
                st.markdown("##### Aplicar cuestionarios al paciente")
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
                    st.markdown("###### Cuestionarios pendientes")
                    st.dataframe(quest)

                if len(answers) > 0:
                    st.markdown("###### Cuestionarios resueltos")
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
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("##### Cargar archivos")
                    st.write("")
                    st.write("")
                    with st.form(key="upload_file", clear_on_submit=True):

                        uploaded_files = st.file_uploader(
                            "Seleccione el archivo a subir", accept_multiple_files=True,
                        )
                        submit = st.form_submit_button("Cargar archivo")
                if submit:
                    for uploaded_file in uploaded_files:
                        bytes_data = uploaded_file.read()
                        folder_name = str(st.session_state.patient_id) + '_' + str(date_from_selected_encounter)
                        folder_path = os.path.join("bin", folder_name)
                        if not os.path.exists(folder_path):
                            os.makedirs(folder_path)
                        file_path = os.path.join(folder_path, uploaded_file.name)
                        try:
                            with open(file_path, "wb") as binary_file:
                                # Write bytes to file
                                binary_file.write(bytes_data)
                            update_attachment(st.session_state.db_engine, st.session_state.patient_id,
                                              date_from_selected_encounter, file_path)
                            st.success("El archivo ha sido cargado con éxito")
                            time.sleep(1)
                        except InterruptedError:
                            print(InterruptedError)
                            st.error("Existió un error al cargar el archivo, intentelo nuevamente")
                            time.sleep(2)
                    st.experimental_rerun()
                with col2:
                    st.markdown("##### Lista de archivos")
                    attachments_list = get_attachments_list(st.session_state.db_engine, st.session_state.patient_id,
                                                            date_from_selected_encounter)
                    attachments_df = pd.DataFrame(attachments_list, columns=["Nombre"])
                    builder = GridOptionsBuilder.from_dataframe(attachments_df)
                    builder.configure_selection(
                        selection_mode="single", use_checkbox=True
                    )

                    gridoptions = builder.build()

                    attached_file_selected = AgGrid(
                        attachments_df,
                        gridOptions=gridoptions,
                        fit_columns_on_grid_load=True,
                        columns_auto_size_mode=True,
                        enable_enterprise_modules=False,
                        update_mode=GridUpdateMode.SELECTION_CHANGED,

                    )
                    if len(attached_file_selected.selected_rows) > 0:
                        file_path = attached_file_selected.selected_rows[0]["Nombre"]
                        with open(file_path, 'rb') as f:
                            data = f.read()

                        st.download_button(
                            label='Descargar archivo',
                            data=data,
                            file_name=file_path,
                            mime='application/octet-stream'
                        )

            with diagnosticos:  # TODO add diagnostic list to encounter table
                diagnostics_list = get_diagnostics(
                    st.session_state.db_engine,
                    st.session_state.patient_id,
                    encounter_selected.date,
                )
                col1, col2 = st.columns([1,1])
                with col1:
                    st.markdown("##### Agregar un diagnóstico")
                    with st.form(key="new_diagnostic", clear_on_submit=True):
                        diagnostic = st.text_input("###### Escriba un diagnóstico preliminar o final")
                        exam_type = st.radio("Select Exam Type", ('Preliminar', 'Final'))
                        submit = st.form_submit_button("Guardar")
                if submit:
                    try:
                        if diagnostic == "":
                            raise Exception("")
                        add_diagnostic(
                            st.session_state.db_engine,
                            date=encounter_selected.date,
                            patient_id=st.session_state.patient_id,
                            diagnostic=diagnostic,
                            type=exam_type
                        )
                        st.success("Diágnostico agregado con éxito")
                        time.sleep(0.7)

                    except:
                        st.error("El campo del diagnóstico no puede estar vacío")
                        time.sleep(2)

                    st.experimental_rerun()

                with col2:
                    st.markdown("##### Lista de diagnósticos")
                    st.experimental_data_editor(
                        diagnostics_list.set_index(diagnostics_list.columns[0]),
                        use_container_width=True
                    )

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
        # edit_personal_info = st.button("Editar", key="editar_datos")

        if False:
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
    with st.expander("**Información adicional**"):
        st.write(patient.extra_information)


def change_view_encounter_history_no_id_with_rerun():
    st.session_state.current_view = "Historial"
    st.session_state.edit_encounter = False
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

    patient_search_results = get_all_patients(st.session_state.db_engine)
    st.markdown("##### Seleccione el paciente a visualizar")
    st.markdown("###### Puede buscar pacientes usando cualquiera de los campos")
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
    other_options = {'suppressColumnVirtualisation': True}
    builder.configure_grid_options(**other_options)
    builder.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=8)
    gridoptions = builder.build()
    with col1:
        if st.session_state.current_view != "Historial":
            patients_found = AgGrid(
                df_patient_search_results,
                gridOptions=gridoptions,
                fit_columns_on_grid_load=True,
                enable_enterprise_modules=False,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                enable_quicksearch=True,
                theme=AgGridTheme.STREAMLIT,
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
            )
        selected_patient = patients_found["selected_rows"]

    col2.write("")
    col2.write("")
    if selected_patient != list():
        with st.sidebar:

            st.subheader(selected_patient[0]["Nombre"])
            colored_header("Opciones","")
            if st.button("Historia clínica"):
                st.session_state.current_view = "Historial"
                st.session_state.patient_id = selected_patient[0]["Cédula"]
                st.session_state.previous_page = "Busqueda"
                st.experimental_rerun()

            # if st.button("Generar reporte"): TODO create reports
            #     st.session_state.current_view = "generate_report"
            #     st.write("Reporte")
            #     st.experimental_rerun()

            if st.button("Agendar cita"):
                st.session_state.id_for_appointment = selected_patient[0]["Cédula"]
                switch_page("Agendar_citas")

            # if st.button("Dar de baja"):
            #     st.session_state.current_view = "generate_report"
            #     st.write("Reporte")
            #     st.experimental_rerun()


if st.session_state.current_view == "Historial":
    st.markdown(
        """
       <style>
       [data-testid="stSidebar"][aria-expanded="true"]{
           min-width: 400px;
           max-width: 400px;
       }
       """,
        unsafe_allow_html=True,
    )
    main_patient_info_view.empty()
    with st.container():
        show_encounter_history_view(st.session_state.patient_id)

if st.session_state.current_view == "inicio":
    st.session_state.current_view = "Busqueda"
    switch_page("inicio")
