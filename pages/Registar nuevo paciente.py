import psycopg2
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
        st.subheader("Sistema de encuestas psicológicas")

def connect():
    conn = psycopg2.connect(
        host="localhost",
        database="bienestar",
        user="postgres",
        password="admin")
    return conn

def registrar(cedula,nombres,apellidos,edad,ocupacion,sexo,estado_civil,carrera):
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        nombre = nombres + " " + apellidos
        query = "INSERT INTO paciente(cedula,nombre,edad,ocupacion,sexo,estado_civil,carrera) values('{0}','{1}','{2}','{3}','{4}','{5}','{6}')".format(cedula,nombre,edad,ocupacion,"True",estado_civil,"1")

        cur.execute(query)
        conn.commit()
        st.success("Paciente registrado")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

limpiar()

with st.form("registro",clear_on_submit=True):
    cedula=st.text_input("Cedula")
    nombres=st.text_input("Nombres")
    apellidos=st.text_input("Apellidos")
    edad=st.text_input("Edad")
    ocupacion = st.text_input("Ocupacion")
    sexo = st.radio("Sexo", ("Masculino", "Femenido"))
    estado_civil=st.selectbox("Estado civil",("Soltero","Casado","Divorciado","Viudo"))
    facultad=st.selectbox("Facultad",("Ingeniería","Economía"))
    carrera=st.selectbox("Carrera",("Sistemas","Industrial"))
    submit=st.form_submit_button("Submit")
    if submit:
        registrar(cedula, nombres, apellidos, edad, ocupacion, sexo, estado_civil, carrera)
