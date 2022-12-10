import datetime

import psycopg2
from psycopg2 import errors
from PIL import Image

import streamlit as st

st.set_page_config(layout="centered")


def limpiar():
    membrete = st.empty()
    membrete.empty()
    with membrete.container():
        img = Image.open("ucuenca.png")
        st.image(img, width=200)
        st.header("Departamento de Bienestar Universitario")
        st.subheader("Registro de nuevos pacientes")

def connect():
    conn = psycopg2.connect(
        host="localhost",
        database="bienestar",
        user="postgres",
        password="admin")
    return conn

def registrar(cedula,nombres,apellidos,fecha_nacimiento,ocupacion,sexo,estado_civil,carrera):
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        nombre = nombres + " " + apellidos
        query = "INSERT INTO paciente(cedula,nombre,fecha_nacimiento,ocupacion,sexo,estado_civil) values('{0}','{1}','{2}','{3}','{4}','{5}')".format(cedula,nombre,fecha_nacimiento,ocupacion,"True",estado_civil)

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
            submit=st.form_submit_button("Submit")
            if submit:
                mensaje=registrar(cedula, nombres, apellidos, fecha_nacimiento, ocupacion, sexo, estado_civil)
                return mensaje


limpiar()

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

