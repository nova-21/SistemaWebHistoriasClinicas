import base64
import time
import urllib

import psycopg2
import streamlit as st
from PIL import Image
import pandas as pd

from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode

from utilidades.conexion import connect, buscar_datos_personales, registrar_sesion_db, guardar_archivos, \
    buscar_historial, buscar_sesion

st.set_page_config(layout="centered")


if 'pagina' not in st.session_state:
    st.session_state.pagina = "Busqueda"

if 'cedula' not in st.session_state:
    st.session_state.cedula = " "


membrete = st.empty()
contenedor_general = st.empty()

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
        img = Image.open("ucuenca.png")
        st.image(img, width=200)
        st.header("Departamento de Bienestar Universitario")

def inicio():
    st.session_state.pagina = "Busqueda"

def atras():
    st.session_state.pagina = "Paciente"

def cambiar_pagina_historial():
    st.session_state.pagina = "Historial"

def cambiar_pagina_cita():
    st.session_state.pagina = "Nueva cita"

def cambiar_pagina_paciente(cedula):
    st.session_state.cedula = cedula
    st.session_state.pagina = "Paciente"

def cambiar_pagina_editar():
    st.session_state.pagina = "Editar datos"

def obtener_historial(buscar):
    paciente = buscar_datos_personales(buscar)
    cedula, nombre = paciente[0]
    conn = None
    col1, col2 = st.columns([1, 1])
    try:
        cancelado = st.button("Salir", key="dos", on_click=atras)
        historial = buscar_historial(cedula)
        tabla = pd.DataFrame(historial, columns=["Fecha","Descripción corta"], index=None)
        tabla["Descripción corta"].fillna("", inplace=True)
        builder = GridOptionsBuilder.from_dataframe(tabla)
        builder.configure_column("Fecha", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd')
        builder.configure_selection(selection_mode='single', use_checkbox=True)
        gridoptions = builder.build()

        with st.sidebar:

            st.write("Seleccione la sesión que desea visualizar")
            sesion = AgGrid(tabla, gridOptions=gridoptions, fit_columns_on_grid_load=True, enable_enterprise_modules=False, data_return_mode=DataReturnMode.FILTERED_AND_SORTED)


        sesion_seleccionada = sesion["selected_rows"]

        if sesion_seleccionada:
            fecha = sesion_seleccionada[0]["Fecha"]
            resultado_sesion=buscar_sesion(cedula,fecha)
            st.subheader("Asuntos tratados en la sesión")
            st.write(resultado_sesion[0][0])
            st.subheader("Archivos adjuntos a la sesión")

            archivo_seleccionado = st.selectbox(label="  ",options=("Seleccione el archivo a visualizar","Test 1", "Test 2"))
            if archivo_seleccionado == "Test 1":
                displayPDF("https://www.orimi.com/pdf-test.pdf")
            if archivo_seleccionado == "Test 2":
                displayPDF("https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")

        with col1:
            st.subheader(cedula)
            # if (sexo == False):
            #     st.subheader("Masculino")
            # else:
            #     st.subheader("Femenino")

        with col2:
            st.subheader(nombre)
            # st.subheader(fecha_nacimiento)
            # st.subheader(estado_civil)
            # st.subheader(ocupacion)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def registrar_sesion(cedula):
    placeholder = st.form(key="cita")
    with placeholder:
        fecha = st.date_input("Fecha de cita")
        comentarios = st.text_input("Comentarios")
        asistencia = st.checkbox("Asistió a la cita")
        razon_inasistencia=st.text_input("En caso de no asistir indique la razón:")
        encargado=st.text_area("Qué se abordó en la sesión:")
        archivos=st.file_uploader("Adjuntar archivos:")
        st.form_submit_button(label="Guardar")
        lista_datos=(fecha,comentarios,asistencia,razon_inasistencia,encargado)
        registrar_sesion_db(lista_datos)
        guardar_archivos(archivos)
    cancelado = st.button("Cancelar", on_click=atras)

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
                    col1, col2, col3= st.columns((1, 2, 2))
                    col1.write(resultadosDataframe['Cédula'][x])  # cedula identidad
                    col2.write(resultadosDataframe['Nombre'][x])  # nombre completo
                    button_phold = col3.empty()  # create a placeholder
                    do_action = button_phold.button("Seleccionar", key=x)
                    if do_action:
                        cambiar_pagina_paciente(resultadosDataframe['Cédula'][x])
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

if st.session_state.pagina == "Paciente":
    contenedor_general.empty()
    time.sleep(0.01)

    cedula_busqueda = st.session_state.cedula
    cedula, nombre = buscar_datos_personales(cedula_busqueda)[0]

    with contenedor_general.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader(cedula)
            # if (sexo == False):
            #     st.subheader("Masculino")
            # else:
            #     st.subheader("Femenino")
            # st.subheader(estado_civil)
        with col2:
            st.subheader(nombre)
            # st.subheader(fecha_nacimiento)
            # st.subheader(ocupacion)


        st.subheader("¿Qué desea realizar con el paciente?")
        but1, but2, but3 = st.columns([1, 1, 1])
        but1.button("Registrar sesión", on_click=cambiar_pagina_cita)
        but2.button("Revisar historial", on_click=cambiar_pagina_historial)
        but3.button("Regresar al Inicio", on_click=inicio)

if st.session_state.pagina == "Nueva cita":
    contenedor_general.empty()
    time.sleep(0.01)
    with contenedor_general.container():
        st.header("Registrar nueva cita")
        cedula = st.session_state.cedula
        st.subheader(cedula)
        registrar_sesion(cedula)

if st.session_state.pagina == "Historial":
    contenedor_general.empty()
    time.sleep(0.01)
    with contenedor_general.container():
        st.header("Historial de citas")
        obtener_historial(st.session_state.cedula)

# if st.session_state.pagina == "Modificar datos":
#     st.header("Modificar datos")
#     paciente = st.session_state.paciente
#     cedula, nombre, sexo, fecha_nacimiento, ocupacion, estado_civil = paciente
#     st.text(nombre)
