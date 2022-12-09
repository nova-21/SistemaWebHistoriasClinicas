import base64
import urllib

import psycopg2
import streamlit as st
from PIL import Image
import json
import streamlit_google_oauth as oauth
import pandas as pd

from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="centered")

if 'num' not in st.session_state:
    st.session_state.num = 0
    st.session_state.contador = 0
    st.session_state.pagina = "Busqueda"
    st.session_state.paciente = 0

if 'cedula' not in st.session_state:
    st.session_state.cedula = " "

if 'atras' not in st.session_state:
    st.session_state.atras = " "

if 'login' not in st.session_state:
    st.session_state.atras = None

def cargar_preguntas():
    num = st.session_state.num
    f = open("depresion.json", encoding='utf-8')
    preguntas = json.load(f)
    claves = list(preguntas["seccion"].keys())
    return (preguntas, claves)


def displayPDF(file):
    # Opening file from file path. this is used to open the file from a website rather than local
    with urllib.request.urlopen(file) as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="950" type="application/pdf"></iframe>'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


def limpiar():
    membrete = st.empty()
    membrete.empty()
    with membrete.container():
        img = Image.open("ucuenca.png")
        st.image(img, width=200)
        st.header("Departamento de Bienestar Universitario")


def connect():
    conn = psycopg2.connect(
        host="localhost",
        database="bienestar",
        user="postgres",
        password="admin")
    return conn


def inicio():
    st.session_state.pagina = "Busqueda"

def atras():
    st.session_state.atras = "Cancelar"
    st.session_state.pagina = "Busqueda"


def buscarcedula(buscar):
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        query = "SELECT paciente.cedula,paciente.nombre,carrera.nombre,paciente.sexo,paciente.fecha_nacimiento,paciente.ocupacion,paciente.estado_civil FROM paciente paciente join carrera on carrera=id WHERE cedula='{0}' OR UPPER(paciente.nombre) like UPPER('%{0}%')".format(
            buscar)

        cur.execute(query)
        paciente = cur.fetchone()
        print(paciente)
        if (paciente is None):
            st.warning("El paciente no está registrado")
            link = '[Registrar](http://localhost:8501/Registar_nuevo_paciente)'
            st.markdown(link, unsafe_allow_html=True)
        else:
            st.session_state.paciente = paciente
            cedula, nombre, carrera, sexo, fecha_nacimiento, ocupacion, estado_civil = paciente
            if (cedula == buscar or buscar.upper() in nombre.upper()):
                exito = nombre + "-" + carrera
                st.success(exito)
                st.write("¿Qué desea realizar con el paciente?")
                col1, col2, col3 = st.columns([1,1,4],gap="small")

                with col1:
                    st.button('Nueva cita', on_click=seleccionar_nueva_cita)
                with col2:
                    st.button('Ver historial', on_click=seleccionar_historial)

                # with col3:

                #     st.button('Modificar datos', on_click=seleccionar_modificar_datos)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def obtener_historial(buscar):
    conn = None
    col1, col2 = st.columns([1, 1])
    try:
        conn = connect()
        cur = conn.cursor()

        query = "SELECT to_char(fecha, 'YYYY-MM-DD'),asistencia,motivo_ausencia from cita where paciente='{0}'".format(
            buscar)
        cur.execute(query, buscar)
        historial = cur.fetchall()
        conn.close()
        tabla = pd.DataFrame(historial, columns=["Fecha", "Asistencia", "Motivo Ausencia"], index=None)
        tabla["Motivo Ausencia"].fillna("", inplace=True)
        builder = GridOptionsBuilder.from_dataframe(tabla)
        builder.configure_column("Fecha", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd')
        builder.configure_selection(selection_mode='single', use_checkbox=True)
        gridoptions = builder.build()
        sesion = AgGrid(tabla, gridOptions=gridoptions)

        sesio_seleccionada = sesion["selected_rows"]

        if sesio_seleccionada:
            fecha = sesio_seleccionada[0]["Fecha"]

            conn = connect()
            cur = conn.cursor()
            query2 = "SELECT estado_terapia from cita where paciente='{0}' and fecha='{1}'".format(buscar, fecha)
            cur.execute(query2, buscar)
            estado_terapia = cur.fetchall()
            conn.close()

            st.subheader("Asuntos tratados en la sesión")
            st.write(estado_terapia[0][0])
            st.subheader("Archivos adjuntos a la sesión")

            archivo_seleccionado = st.selectbox("",options=("Seleccione el archivo a visualizar","Test 1", "Test 2"))
            if archivo_seleccionado == "Test 1":
                displayPDF("https://www.orimi.com/pdf-test.pdf")
            if archivo_seleccionado == "Test 2":
                displayPDF("https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf")

        total = len(tabla)
        asistidos = tabla[tabla["Asistencia"] == True].count()
        citas_asistidas = asistidos["Asistencia"]
        ausencias = total - citas_asistidas
        tipos_cita = ['Asistidas', 'Ausente']

        values = [citas_asistidas, ausencias]

        with col1:
            st.subheader(nombre)
            st.subheader(carrera)
            if (sexo == False):
                st.subheader("Masculino")
            else:
                st.subheader("Femenino")

        with col2:
            st.subheader(fecha_nacimiento)
            st.subheader(estado_civil)
            st.subheader(ocupacion)
        cancelado = st.button("Salir", on_click=atras)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def registrar_cita(cedula, nombre):
    placeholder = st.form(key="cita")
    with placeholder:
        fecha = st.date_input("Fecha de cita")
        comentarios = st.text_input("Comentarios")
        asistencia = st.checkbox("Asistió a la cita")
        st.text_input("En caso de no asistir indique la razón:")
        st.text_area("Qué se abordó en la sesión:")
        st.file_uploader("Adjuntar archivos:")
        st.form_submit_button()
    cancelado = st.button("Cancelar", on_click=atras)


def seleccionar_historial():
    st.session_state.pagina = "Historial"


def seleccionar_nueva_cita():
    st.session_state.pagina = "Nueva cita"


def seleccionar_modificar_datos():
    st.session_state.pagina = "Modificar datos"


def main():
    if (st.session_state.num == 0):
        cedula = st.text_input("Cédula")
        if cedula == "0106785215":
            st.text("Es usted Alex Pinos")
            st.button("Si")
        else:
            st.warning("Ingrese una cédula válida")
    else:
        print("ok")

with st.sidebar:
    login_info = oauth.login(
            client_id="418217949250-26re6hs241ls4v3eu3l73i433v53v6mo.apps.googleusercontent.com",
            client_secret="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",
            redirect_uri="http://localhost:8501",
            login_button_text="Inicie sesión con Google",
            logout_button_text="Cerrar sesión",
        )
    st.session_state.login = login_info


limpiar()

if login_info:
    user_id, user_email = login_info
    with st.sidebar as sd:
        st.write(f"{user_email}")


    if user_email == "alex.pinos@ucuenca.edu.ec":
        if st.session_state.pagina == "Busqueda":
            if st.session_state.atras == "Cancelar":

                cedula_anterior = ""
                cedula = st.text_input("Ingrese la cédula o los apellidos del paciente:", value=st.session_state.cedula)
                # buscar = st.button("Buscar paciente")

                buscarcedula(st.session_state.cedula)
                st.session_state.atras = ""
            else:
                cedula_anterior = ""
                cedula = st.text_input("Ingrese la cédula o los apellidos del paciente:")
                # buscar = st.button("Buscar paciente")

                # if buscar == True or (cedula_anterior != cedula):
                if cedula_anterior != cedula:
                    cedula_anterior = cedula
                    buscarcedula(cedula)

        if st.session_state.pagina == "Historial":
            st.header("Historial de citas")
            paciente = st.session_state.paciente
            cedula, nombre, carrera, sexo, fecha_nacimiento, ocupacion, estado_civil = paciente
            obtener_historial(cedula)

        if st.session_state.pagina == "Nueva cita":
            st.header("Registrar nueva cita")
            paciente = st.session_state.paciente
            cedula, nombre, carrera, sexo, fecha_nacimiento, ocupacion, estado_civil = paciente
            st.text(nombre)
            st.session_state.cedula=cedula
            registrar_cita(cedula, nombre)

        # if st.session_state.pagina == "Modificar datos":
        #     st.header("Modificar datos")
        #     paciente = st.session_state.paciente
        #     cedula, nombre, carrera, sexo, fecha_nacimiento, ocupacion, estado_civil = paciente
        #     st.text(nombre)

else:
        st.subheader("Bienvenido al sistema de manejo de historias clínicas psicológicas.")
        st.subheader("Por favor inicie sesión con su cuenta de correo universitaria para continuar.")