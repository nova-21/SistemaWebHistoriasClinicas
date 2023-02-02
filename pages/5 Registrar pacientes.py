import datetime

import psycopg2
from psycopg2 import errors
from PIL import Image
import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid

from utilidades.conexion import buscar_datos_personales, connect

st.set_page_config(layout="centered")

def limpiar():
    membrete = st.empty()
    membrete.empty()
    with membrete.container():
        img = Image.open("ucuenca.png")
        st.image(img, width=200)
        st.header("Dirección de Bienestar Universitario")
        st.subheader("Administración de pacientes")

def registrar(cedula, nombres, apellidos, fecha_nacimiento, ocupacion, estado_civil, facultad, nombre_preferido, lugar_nacimiento, lugar_residencia, contacto_emergencia, telefono_emergencia, antecendentes_familiares, antecendentes_personales, antecendentes_clinicos):

    try:
        conn = connect()
        cur = conn.cursor()
        nombre = nombres + " " + apellidos
        query = "INSERT INTO paciente(cedula,nombre,fecha_nacimiento,ocupacion,estado_civil, facultad, nombre_preferido, lugar_nacimiento, lugar_residencia, contacto_emergencia, telefono_emergencia, antecedentes_familiares, antecedentes_personales, antecedentes_clinicos) values('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}')".format(cedula, nombre, fecha_nacimiento, ocupacion, estado_civil, facultad, nombre_preferido, lugar_nacimiento, lugar_residencia, contacto_emergencia, telefono_emergencia, antecendentes_familiares, antecendentes_personales, antecendentes_clinicos)
        cur.execute(query)
        conn.commit()
        return "Paciente registrado"
    except (Exception, errors.UniqueViolation) as error:
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
            genero = st.text_input("Género")
            fecha_nacimiento = st.date_input("Fecha de nacimiento (Año/Mes/Día)", min_value=datetime.date(1900,1,1))
            ocupacion = st.text_input("Ocupación")
            correo_electronico = st.text_input("Correo electrónico")
            estado_civil=st.selectbox("Estado civil",("Soltero","Casado","Divorciado","Viudo","Union de hecho"))
            facultad=st.text_input("Facultad/Dependencia")
            ciudad_nacimiento = st.text_input("Ciudad de nacimiento")
            ciudad_residencia = st.text_input("Ciudad de residencia")
            direccion = st.text_input("Dirección del domicilio")
            hijos = st.number_input("Número de hijos",min_value=0)
            personas_vive = st.text_input("Personas con las que vive", placeholder="Ingrese las personas separadas con una coma.")
            contacto_emergencia_nombre=st.text_input("Nombre del contacto de emergencia")
            contacto_emergencia_parentezco = st.text_input("Parentezco del contacto de emergencia",help="Por ejemplo: Padre, Madre, Hermano")
            contacto_emergencia_telefono=st.text_input("Teléfono del contacto de emergencia")
            antecendentes_familiares=st.text_area("Antecedentes familiares")
            antecendentes_personales = st.text_area("Antecedentes personales")
            antecendentes_clinicos = st.text_area("Información adicional")
            submit=st.form_submit_button("Registrar")
            if submit:
                try:
                    mensaje = "Paciente registrado"
                except:
                    mensaje = "Paciente registrado"
                    print("Error al registrar usuario")
                return mensaje

limpiar()

registro = st.tabs(["Registrar paciente"])

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



