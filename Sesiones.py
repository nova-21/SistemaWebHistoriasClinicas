import psycopg2
import streamlit as st
from PIL import Image
import json
import pandas as pd
from pandas.io.json import json_normalize
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="centered")

if 'num' not in st.session_state:
    st.session_state.num = 0
    st.session_state.contador = 0
    st.session_state.pagina = "Busqueda"
    st.session_state.paciente=0


def cargar_preguntas():
    num = st.session_state.num
    f = open("depresion.json", encoding='utf-8')
    preguntas = json.load(f)
    claves = list(preguntas["seccion"].keys())
    return (preguntas, claves)


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

def buscarcedula(buscar):
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        query = "SELECT paciente.cedula,paciente.nombre,carrera.nombre,paciente.sexo,paciente.edad,paciente.ocupacion,paciente.estado_civil FROM paciente paciente join carrera on carrera=id WHERE cedula='{0}'".format(buscar)

        cur.execute(query)
        paciente=cur.fetchone()
        if (paciente is None):
            st.warning("El paciente no está registrado")
            link = '[Registrar](http://localhost:8501/Registar_nuevo_paciente)'
            st.markdown(link, unsafe_allow_html=True)
        else:
            st.session_state.paciente=paciente
            cedula, nombre, carrera, sexo,edad,ocupacion,estado_civil = paciente
            if (cedula == buscar):
                exito = nombre + "-" + carrera
                st.success(exito)
                col1, col2, col3 = st.columns(3)

                with col1:
                    historial=st.button('Historial', on_click=seleccionar_historial)

                with col2:
                    nueva_cita=st.button('Nueva cita',on_click=seleccionar_nueva_cita)

                with col3:
                    modificar_datos=st.button('Modificar datos', on_click=seleccionar_modificar_datos)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def obtener_historial(buscar):
    conn = None
    col1, col2 = st.columns([1,1])
    try:
        conn = connect()
        cur = conn.cursor()

        query = "SELECT to_char(fecha, 'YYYY-MM-DD'),asistencia,motivo_ausencia,responsable from cita where paciente='{0}'".format(buscar)
        cur.execute(query,buscar)
        historial = cur.fetchall()
        conn.close()
        tabla=pd.DataFrame(historial, columns=["Fecha","Asistencia","Motivo Ausencia","Responsable"], index=None)
        tabla["Motivo Ausencia"].fillna("", inplace=True)
        builder=GridOptionsBuilder.from_dataframe(tabla)
        builder.configure_column("Fecha", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd')
        builder.configure_selection(selection_mode='single',use_checkbox=True)
        gridoptions=builder.build()
        sesion=AgGrid(tabla,gridOptions=gridoptions)

        sesio_seleccionada=sesion["selected_rows"]

        if sesio_seleccionada:
            fecha=sesio_seleccionada[0]["Fecha"]

            conn = connect()
            cur = conn.cursor()
            query2 = "SELECT estado_terapia from cita where paciente='{0}' and fecha='{1}'".format(buscar,fecha)
            cur.execute(query2, buscar)
            estado_terapia = cur.fetchall()
            conn.close()

            st.subheader("Asuntos tratados en la sesión")
            estado_terapia[0][0]

            st.subheader("Archivos adjuntos a la sesión")

        total=len(tabla)
        asistidos=tabla[tabla["Asistencia"]==True].count()
        citas_asistidas=asistidos["Asistencia"]
        ausencias=total-citas_asistidas
        tipos_cita = ['Asistidas', 'Ausente']

        values = [citas_asistidas, ausencias]


        with col1:
            st.subheader(nombre)
            st.subheader(carrera)
            if(sexo==False):
                st.subheader("Masculino")
            else:
                st.subheader("Femenino")

        with col2:
            st.subheader(edad)
            st.subheader(estado_civil)
            st.subheader(ocupacion)
        cancelado = st.button("Salir", on_click=inicio)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')



def registrar_cita(cedula,nombre):
    placeholder = st.form(key="cita")
    with placeholder:
        fecha=st.date_input("Fecha de cita")
        comentarios=st.text_input("Comentarios")
        asistencia=st.checkbox("Asistió a la cita")
        st.text_input("En caso de no asistir indique la razón:")
        st.text_area("Qué se abordó en la sesión:")
        st.file_uploader("Adjuntar archivos:")
        st.form_submit_button()
    cancelado=st.button("Cancelar",on_click=inicio())

def seleccionar_historial():
    st.session_state.pagina = "Historial"
def seleccionar_nueva_cita():
    st.session_state.pagina = "Nueva cita"
def seleccionar_modificar_datos():
    st.session_state.pagina = "Modificar datos"


def main():
    if (st.session_state.num == 0):
        cedula = st.text_input("Cédula")
        if (cedula == "0106785215"):
            st.text("Es usted Alex Pinos")
            st.button("Si")
        else:
            st.warning("Ingrese una cédula válida")
    else:
        print("ok")

limpiar()

if(st.session_state.pagina=="Busqueda"):
    cedula_anterior=""
    cedula = st.text_input("Ingrese la cédula del paciente:")
    buscar=st.button("Buscar paciente")

    if buscar==True or (cedula_anterior != cedula):
        cedula_anterior=cedula
        buscarcedula(cedula)

if(st.session_state.pagina=="Historial"):
    st.header("Historial de citas")
    paciente=st.session_state.paciente
    cedula, nombre, carrera, sexo, edad, ocupacion, estado_civil = paciente
    obtener_historial(cedula)

if(st.session_state.pagina=="Nueva cita"):
    st.header("Registrar nueva cita")
    paciente = st.session_state.paciente
    cedula, nombre, carrera, sexo, edad, ocupacion, estado_civil = paciente
    st.text(nombre)
    registrar_cita(cedula, nombre)

if(st.session_state.pagina=="Modificar datos"):
    st.header("Modificar datos")
    paciente = st.session_state.paciente
    cedula, nombre, carrera, sexo, edad, ocupacion, estado_civil = paciente
    st.text(nombre)
