import base64
import datetime
import time
import urllib
from datetime import datetime, date
import streamlit as st
from PIL import Image
import pandas as pd

from streamlit_extras.colored_header import colored_header
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode

from utilidades.conexion import (
    buscar_datos_personales,
    registrar_sesion_db,
    buscar_historial,
    buscar_sesion,
    buscar_datos_personales2,
)

st.set_page_config(layout="centered")

if "pagina" not in st.session_state:
    st.session_state.pagina = "Busqueda"

if "cedula" not in st.session_state:
    st.session_state.cedula = " "

if "registrar" not in st.session_state:
    st.session_state.registrar = " "

if "sesion_seleccionada" not in st.session_state:
    st.session_state.sesion_seleccionada = " "

membrete = st.empty()
contenedor_general = st.empty()
with st.sidebar:
    contenedor_controles = st.empty()
    contenedor_sesiones = st.empty()


def displayPDF(file):
    # Opening file from file path. this is used to open the file from a website rather than local
    with urllib.request.urlopen(file) as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")

    # Embedding PDF in HTML
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="950" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


def limpiar():
    membrete.empty()
    with membrete.container():
        img = Image.open("resources/ucuenca.png")
        st.image(img, width=200)
        st.header("Dirección de Bienestar Universitario")


def inicio():
    st.session_state.pagina = "Busqueda"


def atras():
    st.session_state.pagina = "Paciente"


def cambiar_pagina_historial(cedula):
    st.session_state.cedula = cedula
    st.session_state.pagina = "Historial"


def cambiar_pagina_cita():
    st.session_state.pagina = "Nueva cita"


def cambiar_pagina_paciente(cedula):
    st.session_state.cedula = cedula
    st.session_state.pagina = "Paciente"


def tab_registrar():
    st.session_state.registrar = True


def cambiar_pagina_editar():
    st.session_state.pagina = "Editar datos"


def obtener_historial(buscar, sesion_seleccionada=None):
    # st.header("Historial de sesiones")
    paciente = buscar_datos_personales2(buscar)
    (
        cedula,
        nombre,
        fecha_nacimiento,
        ocupacion,
        estado_civil,
        facultad,
        antecedentes_familiares,
        antecedentes_personales,
        antecedentes_clinicos,
        lugar_residencia,
        nombre_preferido,
        contacto_emergencia,
        telefono_emergencia,
    ) = paciente
    historial = buscar_historial(cedula)
    tabla = pd.DataFrame(historial, columns=["Fecha", "Descripción corta"], index=None)
    tabla["Descripción corta"].fillna("", inplace=True)
    builder = GridOptionsBuilder.from_dataframe(tabla)
    builder.configure_column(
        "Fecha", type=["customDateTimeFormat"], custom_format_string="yyyy-MM-dd"
    )
    builder.configure_selection(selection_mode="multiple", use_checkbox=False)
    builder.configure_side_bar(filters_panel=False)
    if st.session_state.sesion_seleccionada != " ":
        builder.configure_selection(pre_selected_rows=[0])
    gridoptions = builder.build()

    with contenedor_controles.container():
        colored_header(label="Controles", color_name="red-50", description="")
        st.button(
            "🏠 Regresar a la búsqueda de pacientes",
            type="primary",
            key="dos",
            on_click=inicio,
        )
        st.button("Registrar nueva sesión", on_click=tab_registrar)
        editar_sesion = st.button("Editar datos de la sesión")

    with st.sidebar:
        colored_header(
            label="Historial de sesiones", color_name="red-50", description=""
        )

        st.write("Seleccione la sesión que desea visualizar")

        sesion = AgGrid(
            tabla,
            gridOptions=gridoptions,
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=False,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
        )

    sesion_seleccionada = sesion["selected_rows"]

    if st.session_state.registrar == True:
        st.header("Registrar nueva cita")
        registrar_sesion()
    st.subheader("_Paciente: " + nombre+"_")

    if sesion_seleccionada:
        fecha_seleccionada = sesion_seleccionada[0]["Fecha"]
        resultado_sesion = buscar_sesion(cedula, fecha_seleccionada)
        (
            asuntos_tratados,
            cuestionarios_pendientes,
            beck_ansiedad,
            beck_depresion,
        ) = resultado_sesion
        if editar_sesion:
            contenedor_controles.empty()
            with contenedor_controles.container():
                colored_header(label="Controles", color_name="red-50", description="")
                cancelado = st.button(
                    "❌ Cancelar edición",
                    type="primary",
                    on_click=cambiar_pagina_historial_sin_cedula,
                )
                st.write("")
                st.write("")
            placeholder = st.form(key="cita")
            with placeholder:
                fecha = st.date_input(
                    "Fecha de cita",
                    value=datetime.strptime(fecha_seleccionada, "%Y-%m-%d"),
                )
                encargado = st.text_input("Tratante", value="Juan Perez")
                descripcion = st.text_input("Descripción corta de la sesión")
                asistencia = st.text_area(
                    "Asuntos tratados en la sesión", value=asuntos_tratados
                )

                tareas = st.text_input("Tareas enviadas", value="Lorem ipsum")
                archivos = st.file_uploader("Adjuntar archivos:")
                guardar=st.form_submit_button(label="Guardar")

        else:
            colored_header(
                label="Información de la sesión", color_name="red-50", description=""
            )
            st.markdown("#### Fecha de la sesión: " + str(fecha_seleccionada))

            informacion, cuestionarios, archivos_adjuntos = st.tabs(
                ["Información", "Cuestionarios", "Archivos adjuntos"]
            )
            with informacion:
                st.markdown("#### Tratante: Juan Perez")
                st.markdown("#### Asuntos tratados en la sesión")
                st.write(resultado_sesion[0])
                st.markdown("#### Tareas enviadas")
                st.write("Lorem ipsum")

            # with archivos_adjuntos:
            #     st.checkbox("Mostrar archivos adjuntos")
            #     # displayPDF("https://www.orimi.com/pdf-test.pdf")
            beckA = ""
            beckD = ""

            if cuestionarios_pendientes == "0":
                beckA = False
                beckD = False
            if cuestionarios_pendientes == "1":
                beckA = True
                beckD = False
            if cuestionarios_pendientes == "2":
                beckA = False
                beckD = True
            if cuestionarios_pendientes == "3":
                beckA = True
                beckD = True
            with cuestionarios:
                st.markdown("#### Cuestionarios y Escalas")
                st.markdown(
                    "**Seleccione los cuestionarios que desea aplicar al paciente:**"
                )
                if cuestionarios_pendientes is not None:
                    st.checkbox(
                        "Escala de Ansiedad de Beck | BAI",
                        value=beckA,
                        disabled=(
                            not beckA
                            or fecha_seleccionada != str(date.today().isoformat())
                        ),
                    )
                    st.checkbox(
                        "Escala de Depresión de Beck 2 | BDI-II",
                        value=beckD,
                        disabled=(
                            not beckD
                            or fecha_seleccionada != str(date.today().isoformat())
                        ),
                    )
                else:
                    st.checkbox(
                        "Escala de Ansiedad de Beck | BAI",
                        value=beckA,
                        disabled=(
                            beckA or fecha_seleccionada != str(date.today().isoformat())
                        ),
                    )
                    st.checkbox(
                        "Escala de Depresión de Beck 2 | BDI-II",
                        value=beckD,
                        disabled=(
                            beckD or fecha_seleccionada != str(date.today().isoformat())
                        ),
                    )
                if cuestionarios_pendientes == "0" and (
                    beck_depresion == None and beck_ansiedad == None
                ):
                    st.markdown("#### Resultados de Cuestionarios")
                    st.write("No se han asignado cuestionarios en esta sesión")
                else:
                    st.markdown("#### Resultados de Cuestionarios")
                    if beck_depresion == None:
                        beck_depresion = "Pendiente"
                    if beck_ansiedad == None:
                        beck_ansiedad = "Pendiente"
                    lista = pd.DataFrame(
                        {
                            "Cuestionario": ["Ansiedad de Beck", "Depresión de Beck"],
                            "Resultado": [beck_ansiedad, beck_depresion],
                        }
                    )
                    st.dataframe(lista, use_container_width=True)
            with archivos_adjuntos:
                st.markdown("#### Cargar archivos")
                st.file_uploader("Subir nuevos archivos adjuntos")
                st.markdown("#### Descargar archivos guardados")
                st.download_button("Archivo 1", data="Archivo de prueba")
                st.download_button("Archivo 2", data="Archivo de prueba")

    colored_header(label="Datos personales", color_name="red-50", description="")

    with st.expander("**Datos personales**"):
        col1, col2 = st.columns([1, 1])

        editar_datos = st.button("Editar", key="editar_datos")
        editar_datos = False
        if editar_datos:
            # with col1:
            #     with st.form(key="editar datos"):
            #         st.text_input("Este")
            #         st.form_submit_button("Guardar")
            print("Hi")
        else:
            with col1:
                st.write("Cédula: ")
                st.write("Género:")
                st.write("Fecha de nacimiento: ")
                st.write("E-mail:")
                st.write("Facultad de dependencia: ")
                st.write(
                    "Contacto de emergencia: "
                    + " "
                    + " "
                    + " "
                )
                st.write("Parentezco: ")
                st.write("Personas con las que vive:")

            with col2:
                st.write("Nombre preferido: " )
                st.write("Ocupación: " )
                st.write("Estado civil: " )
                st.write("Ciudad de nacimiento: Cuenca")
                st.write("Ciudad de residencia: ")
                st.write("Hijos: ")
                st.write("Dirección:")

    with st.expander("**Antecedentes familiares**"):
        st.write(antecedentes_familiares)
        st.button("Editar", key="editar_familiares")
    with st.expander("**Antecedentes personales**"):
        st.write(antecedentes_personales)
        st.button("Editar", key="editar_personales")
    with st.expander("**Antecedentes clínicos**"):
        st.write(antecedentes_clinicos)
        st.button("Editar", key="editar_clinicos")


def cambiar_pagina_historial_sin_cedula():
    st.session_state.pagina = "Historial"
    st.session_state.registrar = False
    # st.experimental_rerun()


def cambiar_pagina_historial_sin_cedula_normal():
    st.session_state.pagina = "Historial"
    st.session_state.registrar = False


def registrar_sesion():
    contenedor_controles.empty()
    with contenedor_controles.container():
        colored_header(label="Controles", color_name="red-50", description="")

        cancelado = st.button(
            "❌ Cancelar registro",
            type="primary",
            on_click=cambiar_pagina_historial_sin_cedula,
        )
        st.write("")
        st.write("")

    placeholder = st.form(key="cita", clear_on_submit=True)
    with placeholder:
        fecha = st.date_input("Fecha de cita")
        descripcion = st.text_input("Descripción corta")
        asistencia = st.checkbox("¿Asistió a la cita?")
        razon_inasistencia = st.text_input("En caso de no asistir indique la razón:")
        asuntos_tratados = st.text_area("Indique qué se abordó en la sesión:")
        guardar = st.form_submit_button("Guardar")

        if guardar:
            llamar_registro(
                fecha, st.session_state.cedula, asuntos_tratados, descripcion
            )
            cambiar_pagina_historial_sin_cedula()


def llamar_registro(fecha, cedula, asuntos_tratados, descripcion):
    registrar_sesion_db(fecha, cedula, asuntos_tratados, descripcion)


limpiar()

if st.session_state.pagina == "Busqueda":
    contenedor_general.empty()
    time.sleep(0.001)
    with contenedor_general.container():
        valor_busqueda_anterior = ""
        valor_busqueda = st.text_input(
            "Ingrese la cédula o los apellidos del paciente:"
        )
        if valor_busqueda_anterior != valor_busqueda:
            valor_busqueda_anterior = valor_busqueda
            resultado_busqueda = buscar_datos_personales(valor_busqueda)

            if len(resultado_busqueda) == 0:
                st.warning(
                    "No existen resultados. ¿Deseas registrar un nuevo paciente?"
                )
                link = "[Registrar](/Registrar_pacientes)"
                st.markdown(link, unsafe_allow_html=True)
            else:
                resultadosDataframe = pd.DataFrame(
                    resultado_busqueda, columns=["Cédula", "Nombre"], index=None
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
                colms = st.columns((1, 2, 2))
                fields = ["Cédula", "Nombre"]
                for col, field_name in zip(colms, fields):
                    col.write(field_name)

                for x, email in enumerate(resultadosDataframe["Cédula"]):
                    col1, col2, col3 = st.columns((1, 2, 2))
                    col1.write(resultadosDataframe["Cédula"][x])  # cedula identidad
                    col2.write(resultadosDataframe["Nombre"][x])  # nombre completo
                    button_phold = col3.empty()  # create a placeholder
                    do_action = button_phold.button("Seleccionar", key=x)
                    if do_action:
                        cambiar_pagina_historial(resultadosDataframe["Cédula"][x])
                        break


if st.session_state.pagina == "Historial":
    contenedor_general.empty()
    with st.container():
        obtener_historial(st.session_state.cedula)
