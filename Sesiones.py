import base64
import datetime
import time
import urllib
from datetime import datetime, date
import psycopg2
import streamlit as st
from PIL import Image
import pandas as pd

from streamlit_extras.colored_header import colored_header
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode

from utilidades.conexion import connect, buscar_datos_personales, registrar_sesion_db, guardar_archivos, \
    buscar_historial, buscar_sesion, buscar_datos_personales2

st.set_page_config(layout="centered")

if 'pagina' not in st.session_state:
    st.session_state.pagina = "Busqueda"

if 'cedula' not in st.session_state:
    st.session_state.cedula = " "

if 'registrar' not in st.session_state:
    st.session_state.registrar = " "

membrete = st.empty()
contenedor_general = st.empty()
contenedor_historial = st.empty()


def displayPDF(file):
    # Opening file from file path. this is used to open the file from a website rather than local
    with urllib.request.urlopen(file) as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="950" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


def limpiar():
    membrete.empty()
    with membrete.container():
        img = Image.open("resources/ucuenca.png")
        st.image(img, width=200)
        st.header("Departamento de Bienestar Universitario")


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


def obtener_historial(buscar):
    st.header("Historial de citas")
    paciente = buscar_datos_personales2(buscar)
    cedula, nombre, fecha_nacimiento, ocupacion, estado_civil, facultad, antecedentes_familiares, antecedentes_personales, antecedentes_clinicos, lugar_residencia, nombre_preferido, contacto_emergencia, telefono_emergencia = paciente
    historial = buscar_historial(cedula)
    tabla = pd.DataFrame(historial, columns=["Fecha", "Descripción corta"], index=None)
    tabla["Descripción corta"].fillna("", inplace=True)
    builder = GridOptionsBuilder.from_dataframe(tabla)
    builder.configure_column("Fecha", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd')

    builder.configure_selection(selection_mode='single', use_checkbox=True)
    gridoptions = builder.build()

    with st.sidebar:
        st.button("Regresar a la búsqueda", key="dos", on_click=inicio)
        colored_header(
            label="Lista de sesiones previas",
            color_name="red-50",
            description="")
        st.button("Registrar nueva sesión", on_click=tab_registrar)
        st.write("Seleccione la sesión que desea visualizar")
        sesion = AgGrid(tabla, gridOptions=gridoptions, fit_columns_on_grid_load=True, enable_enterprise_modules=False)

    sesion_seleccionada = sesion["selected_rows"]

    with st.sidebar:
        if sesion_seleccionada:
            editar_sesion = st.button("Editar datos de la sesión")
            # st.subheader("Archivos adjuntos a la sesión")
            # archivo_seleccionado = st.selectbox(label="Seleccione el archivo a visualizar",
            #                                     options=("Seleccionar", "Test 1", "Test 2"))

    if st.session_state.registrar == True:
        st.header("Registrar nueva cita")
        registrar_sesion()

    if sesion_seleccionada:
        fecha_seleccionada = sesion_seleccionada[0]["Fecha"]
        resultado_sesion = buscar_sesion(cedula, fecha_seleccionada)
        asuntos_tratados, cuestionarios_pendientes, beck_ansiedad, beck_depresion = resultado_sesion
        if editar_sesion:
            placeholder = st.form(key="cita")
            with placeholder:
                fecha = st.date_input("Fecha de cita", value=datetime.strptime(fecha_seleccionada, '%Y-%m-%d'))
                encargado = st.text_input("Tratante", value="Juan Perez")
                asistencia = st.text_area("Asuntos tratados en la sesión", value=asuntos_tratados)
                archivos = st.file_uploader("Adjuntar archivos:")
                st.form_submit_button(label="Guardar")
        else:
            colored_header(
                label="Información de la sesión",
                color_name="red-50",
                description="")
            informacion, cuestionarios, archivos_adjuntos  = st.tabs(
                ["Información", "Cuestionarios", "Archivos adjuntos"])
            with informacion:
                st.subheader("Fecha: " + str(fecha_seleccionada))
                st.subheader("Tratante: Juan Perez")
                st.subheader("Asuntos tratados en la sesión")
                st.write(resultado_sesion[0])

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
                st.subheader("Cuestionarios y Escalas")
                st.markdown("**Seleccione los cuestionarios que desea aplicar al paciente:**")
                st.checkbox("Escala de Ansiedad de Beck | BAI", value=beckA, disabled=(not beckA or fecha_seleccionada != str(date.today().isoformat())))
                st.checkbox("Escala de Depresión de Beck 2 | BDI-II", value=beckD, disabled=(not beckD or fecha_seleccionada != str(date.today().isoformat())))
                if cuestionarios_pendientes == "0" and (beck_depresion == None and beck_ansiedad == None):
                    st.subheader("Resultados de Cuestionarios")
                    st.write("No se han asignado cuestionarios en esta sesión")
                else:
                    st.subheader("Resultados de Cuestionarios")
                    if beck_depresion == None:
                        beck_depresion = "Pendiente"
                    if beck_ansiedad == None:
                        beck_ansiedad = "Pendiente"
                    lista = pd.DataFrame(
                        {
                            "Cuestionario": ["Ansiedad de Beck", "Depresión de Beck"],
                            "Resultado": [beck_ansiedad, beck_depresion]
                        })
                    st.dataframe(lista, use_container_width=True)

    colored_header(
        label="Datos personales",
        color_name="red-50",
        description=""
    )

    st.subheader("Nombre completo: " + nombre)

    with st.expander("Datos Personales"):
        col1, col2 = st.columns([1, 1])
        with col1:
            # if (sexo == False):
            #     st.subheader("Masculino")
            # else:
            #     st.subheader("Femenino")
            st.write("Cédula: " + cedula)
            st.write("Fecha de nacimiento: " + str(fecha_nacimiento))
            st.write("Facultad de dependencia: " + str(facultad))
            st.write("Contacto de emergencia: "+ contacto_emergencia + " "+ telefono_emergencia)
        with col2:
            st.write("Nombre preferido: " + nombre_preferido)
            st.write("Ocupación: " + ocupacion)
            st.write("Estado civil: " + estado_civil)
            st.write("Residencia: "+ lugar_residencia)

    with st.expander("Antecedentes familiares"):
        st.write(antecedentes_familiares)
    with st.expander("Antecedentes personales"):
        st.write(antecedentes_personales)
    with st.expander("Antecedentes clínicos"):
        st.write(antecedentes_clinicos)


def cambiar_pagina_historial_sin_cedula():
    st.session_state.pagina = "Historial"
    st.session_state.registrar = False
    st.experimental_rerun()
def cambiar_pagina_historial_sin_cedula_normal():
    st.session_state.pagina = "Historial"
    st.session_state.registrar = False


def registrar_sesion():
    with st.sidebar:
        cancelado = st.button("Cancelar y regresar al historial", on_click=cambiar_pagina_historial_sin_cedula)

    placeholder = st.form(key="cita", clear_on_submit=True)
    with placeholder:
        fecha = st.date_input("Fecha de cita")
        descripcion = st.text_input("Descripción corta")
        asistencia = st.checkbox("¿Asistió a la cita?")
        razon_inasistencia = st.text_input("En caso de no asistir indique la razón:")
        asuntos_tratados = st.text_area("Indique qué se abordó en la sesión:")
        guardar=st.form_submit_button("Guardar")

        if guardar:
            llamar_registro(fecha, st.session_state.cedula, asuntos_tratados, descripcion)
            cambiar_pagina_historial_sin_cedula()

def llamar_registro(fecha, cedula, asuntos_tratados,descripcion):
    registrar_sesion_db(fecha, cedula,asuntos_tratados,descripcion)

limpiar()

if st.session_state.pagina == "Busqueda":
    contenedor_general.empty()
    time.sleep(0.001)
    with contenedor_general.container():
        valor_busqueda_anterior = ""
        valor_busqueda = st.text_input("Ingrese la cédula o los apellidos del paciente:")
        if valor_busqueda_anterior != valor_busqueda:
            valor_busqueda_anterior = valor_busqueda
            resultado_busqueda = buscar_datos_personales(valor_busqueda)

            if (len(resultado_busqueda) == 0):
                st.warning("No existen resultados. ¿Deseas registrar un nuevo paciente?")
                link = '[Registrar](http://localhost:8501/Registar_nuevo_paciente)'
                st.markdown(link, unsafe_allow_html=True)
            else:
                resultadosDataframe = pd.DataFrame(resultado_busqueda, columns=['Cédula', 'Nombre'], index=None)
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
                fields = ["Cédula", 'Nombre']
                for col, field_name in zip(colms, fields):
                    col.write(field_name)

                for x, email in enumerate(resultadosDataframe['Cédula']):
                    col1, col2, col3 = st.columns((1, 2, 2))
                    col1.write(resultadosDataframe['Cédula'][x])  # cedula identidad
                    col2.write(resultadosDataframe['Nombre'][x])  # nombre completo
                    button_phold = col3.empty()  # create a placeholder
                    do_action = button_phold.button("Seleccionar", key=x)
                    if do_action:
                        cambiar_pagina_historial(resultadosDataframe['Cédula'][x])
                        break
        # if cita and len(paciente_seleccionado)>0:
        #
        #     cedula_seleccion = paciente_seleccionado[0]["Cédula"]
        #     st.session_state.cedula=cedula_seleccion
        #     seleccionar_nueva_cita()
        #
        # if historial and len(paciente_seleccionado)>0:
        #     cedula_seleccion = paciente_seleccionado[0]["Cédula"]
        #     st.session_state.cedula=cedula_seleccion
        #     seleccionar_historial()

# if st.session_state.pagina == "Paciente":
#     contenedor_general.empty()
#     time.sleep(0.01)
#
#     cedula_busqueda = st.session_state.cedula
#     cedula, nombre = buscar_datos_personales(cedula_busqueda)[0]
#
#     with contenedor_general.container():
#         st.subheader(nombre)
#         # col1, col2 = st.columns([1, 1])
#         # with col1:
#         #     st.subheader(cedula)
#             # if (sexo == False):
#             #     st.subheader("Masculino")
#             # else:
#             #     st.subheader("Femenino")
#             # st.subheader(estado_civil)
#         # with col2:
#
#             # st.subheader(fecha_nacimiento)
#             # st.subheader(ocupacion)
#
#
#         st.subheader("¿Qué desea realizar con el paciente?")
#         but1, but2, but3 = st.columns([1, 1, 1])
#         but1.button("Registrar sesión", on_click=cambiar_pagina_cita)
#         but2.button("Revisar historial", on_click=cambiar_pagina_historial)
#         but3.button("Regresar al Inicio", on_click=inicio)




if st.session_state.pagina == "Historial":
    contenedor_general.empty()
    with st.container():
        obtener_historial(st.session_state.cedula)

# if st.session_state.pagina == "Modificar datos":
#     st.header("Modificar datos")
#     paciente = st.session_state.paciente
#     cedula, nombre, sexo, fecha_nacimiento, ocupacion, estado_civil = paciente
#     st.text(nombre)
