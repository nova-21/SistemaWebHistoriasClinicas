import datetime

import psycopg2
from psycopg2 import errors
from PIL import Image
import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid

from utilidades.conexion import buscar_datos_personales

st.set_page_config(layout="centered")


def limpiar():
    membrete = st.empty()
    membrete.empty()
    with membrete.container():
        img = Image.open("ucuenca.png")
        st.image(img, width=200)
        st.header("Departamento de Bienestar Universitario")
        st.subheader("Administración de pacientes")

def connect():
    conn = psycopg2.connect(
        host="localhost",
        database="bienestar",
        user="postgres",
        password="admin")
    return conn

def registrar(cedula, nombres, apellidos, fecha_nacimiento, ocupacion, estado_civil, facultad, nombre_preferido, lugar_nacimiento, lugar_residencia, contacto_emergencia, telefono_emergencia, antecendentes_familiares, antecendentes_personales, antecendentes_clinicos):
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        nombre = nombres + " " + apellidos
        query = "INSERT INTO paciente(cedula,nombre,fecha_nacimiento,ocupacion,estado_civil,facultad, nombre_preferido, lugar_nacimiento, lugar_residencia, contacto_emergencia, telefono_emergencia, antecedentes_familiares, antecedentes_personales, antecedentes_cinicos values('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}','{14}','{15}')".format(cedula, nombres, apellidos, fecha_nacimiento, ocupacion, estado_civil, facultad, nombre_preferido, lugar_nacimiento, lugar_residencia, contacto_emergencia, telefono_emergencia, antecendentes_familiares, antecendentes_personales, antecendentes_clinicos)

        cur.execute(query)
        conn.commit()
        base.empty()

        return "Paciente registrado"
    except (Exception, errors.UniqueViolation) as error:
        print(error)
        return("El paciente ya se encuentra registrado")
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')



def registrar_paciente(base):

    with base:
        mensaje="Error en el registro"
        with st.form("registro",clear_on_submit=True):
            cedula=st.text_input("Cédula")
            nombres=st.text_input("Nombres")
            apellidos=st.text_input("Apellidos")
            nombre_preferido = st.text_input("Nombre preferido")
            fecha_nacimiento = st.date_input("Fecha de nacimiento (Año/Mes/Día)", min_value=datetime.date(1900,1,1))
            ocupacion = st.text_input("Ocupación")
            lugar_nacimiento = st.text_input("Lugar de nacimiento")
            lugar_residencia = st.text_input("Lugar de residencia")
            sexo = st.radio("Sexo", ("Masculino", "Femenido"))
            estado_civil=st.selectbox("Estado civil",("Soltero","Casado","Divorciado","Viudo"))
            facultad=st.selectbox("Facultad de Dependencia",("Ingeniería","Economía"))

            contacto_emergencia=st.text_input("Nombre del contacto de emergencia")
            telefono_emergencia=st.text_input("Teléfono del contacto de emergencia")
            antecendentes_familiares=st.text_area("Antecedentes familiares")
            antecendentes_personales = st.text_area("Antecedentes personales")
            antecendentes_clinicos = st.text_area("Antecedentes clínicos")
            submit=st.form_submit_button("Submit")
            if submit:
                mensaje=registrar(cedula, nombres, apellidos, fecha_nacimiento, ocupacion, sexo, estado_civil, facultad, nombre_preferido, lugar_nacimiento, lugar_residencia, contacto_emergencia, telefono_emergencia, antecendentes_familiares, antecendentes_personales, antecendentes_clinicos)
                return mensaje


limpiar()

registro, edicion = st.tabs(["Registrar paciente", "Editar paciente"])

with registro:
    base = st.empty()
    mensaje=registrar_paciente(base)

    if mensaje == "Paciente registrado":
        base.empty()
        st.success(mensaje)
        st.button("Aceptar")
    if mensaje == "El paciente ya se encuentra registrado":
        base.empty()
        st.error(mensaje)
        st.button("Aceptar")

with edicion:
    cedula=st.text_input("Buscar al paciente")
    resultado_busqueda = buscar_datos_personales(cedula)

    if (len(resultado_busqueda) == 0):
        st.warning("No existen resultados. ¿Deseas registrar un nuevo paciente?")
        link = '[Registrar](http://localhost:8501/Registar_nuevo_paciente)'
        st.markdown(link, unsafe_allow_html=True)
    else:
        resultadosDataframe = pd.DataFrame(resultado_busqueda, columns=['Cédula', 'Nombre'], index=None)
        builder = GridOptionsBuilder.from_dataframe(resultadosDataframe)
        builder.configure_column("Nacimiento", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd')
        builder.configure_selection(selection_mode='single', use_checkbox=True)
        gridoptions = builder.build()
        pacientes=AgGrid(resultadosDataframe, gridOptions=gridoptions, enable_enterprise_modules=False,
                            fit_columns_on_grid_load=True)
        paciente_seleccionado = pacientes["selected_rows"]
        print(paciente_seleccionado)


