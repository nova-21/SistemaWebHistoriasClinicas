import base64
import datetime
import os
import time
import urllib
from datetime import datetime
import streamlit as st
from PIL import Image
import pandas as pd
from sqlalchemy import create_engine
from streamlit_extras.colored_header import colored_header
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from data.actions.encounter_actions import (
    add_encounter,
    get_encounter_history,
    get_encounter,
)
from data.actions.patient_actions import get_patient_search, get_patient
from data.create_database import Encounter

from utilidades.lists import list_encounter_types

if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine(os.environ.get("DATABASE"))

if "current_view" not in st.session_state:
    st.session_state.current_view = "Busqueda"

if "patient_id" not in st.session_state:
    st.session_state.patient_id = " "

if "register_encounter_page" not in st.session_state:
    st.session_state.register_encounter_page = " "

if "sesion_seleccionada" not in st.session_state:
    st.session_state.encounter_row_selected = " "

membrete = st.empty()
main_patient_info_view = st.empty()
with st.sidebar:
    controls_container = st.empty()
    contenedor_sesiones = st.empty()


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


def show_header():
    membrete.empty()
    with membrete.container():
        img = Image.open("resources/ucuenca.png")
        st.image(img, width=200)
        st.header("Dirección de Bienestar Universitario")


def inicio():
    st.session_state.current_view = "Busqueda"


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
    # st.header("Historial de sesiones")
    patient = get_patient(
        st.session_state.db_engine, id_to_search
    )  # Returns  object type Patient() to facilitate accessing patients data

    encounter_history_list = get_encounter_history(
        st.session_state.db_engine, patient.id
    )

    # astype because dataframes datatypes have issues being cast to be rendered
    df_encounter_list = pd.DataFrame(
        encounter_history_list, columns=["Fecha", "Tipo de atención"], index=None
    ).astype(str)
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
            "🏠 Regresar a la búsqueda de pacientes",
            type="primary",
            key="dos",
            on_click=inicio,
        )
        st.button("Registrar nueva sesión", on_click=tab_registrar)
        edit_encounter = st.button("Editar datos de la sesión")

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
        # (
        #     topics_boarded,
        #     cuestionarios_pendientes,
        #     beck_ansiedad,
        #     beck_depresion,
        # ) = encounter_selected

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

                st.table(df_encounter_list)

            # beckA = ""
            # beckD = ""
            #
            # if cuestionarios_pendientes == "0":
            #     beckA = False
            #     beckD = False
            # if cuestionarios_pendientes == "1":
            #     beckA = True
            #     beckD = False
            # if cuestionarios_pendientes == "2":
            #     beckA = False
            #     beckD = True
            # if cuestionarios_pendientes == "3":
            #     beckA = True
            #     beckD = True
            #
            # with cuestionarios:
            #     st.markdown("#### Cuestionarios y Escalas")
            #     st.markdown(
            #         "**Seleccione los cuestionarios que desea aplicar al paciente:**"
            #     )
            #     if cuestionarios_pendientes is not None:
            #         st.checkbox(
            #             "Escala de Ansiedad de Beck | BAI",
            #             value=beckA,
            #             disabled=(
            #                 not beckA
            #                 or fecha_seleccionada != str(date.today().isoformat())
            #             ),
            #         )
            #         st.checkbox(
            #             "Escala de Depresión de Beck 2 | BDI-II",
            #             value=beckD,
            #             disabled=(
            #                 not beckD
            #                 or fecha_seleccionada != str(date.today().isoformat())
            #             ),
            #         )
            #     else:
            #         st.checkbox(
            #             "Escala de Ansiedad de Beck | BAI",
            #             value=beckA,
            #             disabled=(
            #                 beckA or fecha_seleccionada != str(date.today().isoformat())
            #             ),
            #         )
            #         st.checkbox(
            #             "Escala de Depresión de Beck 2 | BDI-II",
            #             value=beckD,
            #             disabled=(
            #                 beckD or fecha_seleccionada != str(date.today().isoformat())
            #             ),
            #         )
            #     if cuestionarios_pendientes == "0" and (
            #         beck_depresion == None and beck_ansiedad == None
            #     ):
            #         st.markdown("#### Resultados de Cuestionarios")
            #         st.write("No se han asignado cuestionarios en esta sesión")
            #     else:
            #         st.markdown("#### Resultados de Cuestionarios")
            #         if beck_depresion == None:
            #             beck_depresion = "Pendiente"
            #         if beck_ansiedad == None:
            #             beck_ansiedad = "Pendiente"
            #         lista = pd.DataFrame(
            #             {
            #                 "Cuestionario": ["Ansiedad de Beck", "Depresión de Beck"],
            #                 "Resultado": [beck_ansiedad, beck_depresion],
            #             }
            #         )
            #         st.dataframe(lista, use_container_width=True)

            with archivos_adjuntos:
                st.markdown("#### Cargar archivos")
                st.file_uploader("Subir nuevos archivos adjuntos")
                st.markdown("#### Descargar archivos guardados")
                st.download_button("Archivo 1", data="Archivo de prueba")
                st.download_button("Archivo 2", data="Archivo de prueba")

            with diagnosticos:  # TODO add diagnostic list to encounter table
                diag = ["Trastorno obsesivo compulsivo", "Ansiedad moderada"]
                st.dataframe(
                    diag,
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
    with st.expander("**Antecedentes personales**"):
        st.write(patient.personal_history)
        st.button("Editar", key="editar_personales")
    with st.expander("**Antecedentes familiares**"):
        st.write(patient.family_history)
        st.button("Editar", key="editar_familiares")
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
            encounter.practitioner_id = "0106785223"
            submit = st.form_submit_button("Guardar")

    if submit:
        add_encounter(st.session_state.db_engine, encounter)
        with register_encounter_container.empty():
            st.success(
                "La sesión fue grabada con éxito"
            )  # sleep because st.success needs time to be read by the user to move fordward
            time.sleep(1)
        change_view_encounter_history_no_id_with_rerun()


show_header()

if (
    st.session_state.current_view == "Busqueda"
):  # TODO Change patient search to also direct to the user individual report
    main_patient_info_view.empty()
    time.sleep(0.001)
    with main_patient_info_view.container():
        previous_search_value = ""
        search_value = st.text_input("Ingrese la cédula o los apellidos del paciente:")
        if (
            previous_search_value != search_value
        ):  # To avoid patient search running again if text typed by the user hasn't changed
            previous_search_value = search_value
            patient_search_results = get_patient_search(
                st.session_state.db_engine, search_value
            )

            if len(patient_search_results) == 0:
                st.warning(
                    "No existen resultados. ¿Deseas registrar un nuevo paciente?"
                )
                link = "[Registrar](/Registrar_pacientes)"
                st.markdown(link, unsafe_allow_html=True)
            else:
                st.markdown("##### Seleccione el paciente a visualizar")

                df_patient_search_results = pd.DataFrame(
                    patient_search_results,
                    columns=["Cédula", "Nombre1", "Nombre2", "Apellido1", "Apellido2"],
                    index=None,
                )
                # builder = GridOptionsBuilder.from_dataframe(tabla)
                # builder.configure_column("Nacimiento", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd')
                # builder.configure_selection(selection_mode='single', use_checkbox=True)
                # gridoptions = builder.build()
                # with contenedor_general:
                #     AgGrid(tabla, gridOptions=gridoptions, enable_enterprise_modules=False,
                #                     fit_columns_on_grid_load=True)
                # paciente_seleccionado = pacientes["selected_rows"]

                # # Mostrar tabla de resultados
                colms = st.columns(
                    (1, 2, 2)
                )  # start : these few lines shows the header names under the search bar for the clients
                fields = ["Cédula", "Nombre"]
                for col, field_name in zip(colms, fields):
                    col.write(field_name)  # end

                for x, email in enumerate(
                    df_patient_search_results["Cédula"]
                ):  # Prints the id and name of the patients under the search bar and headers
                    col1, col2, col3 = st.columns((1, 2, 2))
                    col1.write(
                        df_patient_search_results["Cédula"][x]
                    )  # Prints the patient id
                    col2.write(
                        df_patient_search_results["Nombre1"][x]
                        + " "
                        + df_patient_search_results["Nombre2"][x]
                        + " "
                        + df_patient_search_results["Apellido1"][x]
                        + " "
                        + df_patient_search_results["Apellido2"][x]
                    )  # Prints the full name

                    # Creates buttons placeholders
                    # TODO check why placeholder
                    button_phold = (
                        col3.empty()
                    )  # Renders select buttons next to the patients names, and onclick switches views to the patient information view
                    do_action = button_phold.button("Seleccionar", key=x)
                    if do_action:
                        cambiar_pagina_historial(df_patient_search_results["Cédula"][x])
                        break


if st.session_state.current_view == "Historial":
    main_patient_info_view.empty()
    with st.container():
        show_encounter_history_view(st.session_state.patient_id)
