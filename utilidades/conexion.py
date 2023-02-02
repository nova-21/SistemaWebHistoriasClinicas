import psycopg2
import streamlit as st
import sqlite3
from sqlite3 import Error

from psycopg2 import errors


def connect():
    conn = sqlite3.connect(r"./utilidades/bienestar.db")
    return conn

# def connect():
#     conn = psycopg2.connect(
#         host="localhost",
#         database="bienestar",
#         user="postgres",
#         password="admin")
#     return conn


@st.cache
def buscar_datos_personales(datos_personales):
    conn = None
    resultado_busqueda=""
    try:
        conn = connect()
        cur = conn.cursor()
        query = "SELECT paciente.cedula, paciente.nombre FROM paciente WHERE cedula='{0}' OR UPPER(paciente.nombre) like UPPER('%{0}%')".format(
            datos_personales)
        cur.execute(query)
        resultado_busqueda = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
        return resultado_busqueda

@st.cache
def buscar_datos_personales2(cedula):
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        query = "SELECT paciente.cedula, paciente.nombre,fecha_nacimiento, ocupacion, estado_civil, facultad, antecedentes_familiares, antecedentes_personales, antecedentes_clinicos, lugar_residencia, nombre_preferido, contacto_emergencia, telefono_emergencia FROM paciente WHERE cedula='{0}'".format(
            cedula)
        cur.execute(query)
        resultado_busqueda = cur.fetchone()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
        return resultado_busqueda

@st.cache
def buscar_historial(cedula):
    historial=""
    try:
        conn = connect()
        cur = conn.cursor()
        #to_char "YYYY-MM-DD"
        query = "SELECT fecha as date,descripcion from cita where paciente='{0}' order by date desc".format(
            cedula)

        cur.execute(query)
        historial = cur.fetchall()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
        return historial

@st.cache
def buscar_sesion(cedula,fecha):
    sesion = ""
    try:
        conn = connect()
        cur = conn.cursor()
        query = "SELECT asuntos_tratados, cuestionarios_pendientes, beck_ansiedad, beck_depresion from cita where paciente='{0}' and fecha='{1}'".format(cedula, fecha)
        cur.execute(query)
        sesion = cur.fetchone()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
        return sesion

def registrar_sesion_db(fecha, paciente,asuntos_tratados,descripcion):
    try:
        conn = connect()
        cur = conn.cursor()
        print(paciente)
        query = "INSERT INTO cita(fecha,paciente,asuntos_tratados,descripcion) values('{0}','{1}','{2}','{3}')".format(fecha, paciente, asuntos_tratados,descripcion)
        cur.execute(query)
        conn.commit()
        conn.close()
        return "Sesion registrada"
    except (Exception, errors.UniqueViolation) as error:
        return ("Ya existe una sesion")
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def guardar_archivos(archivos):
    ##TODO crear funcion para serializar archivos en disco
    print("Exito")


# def restore():
#     crear_paciente = r"""CREATE TABLE paciente
# (
#   cedula character varying NOT NULL,
#   sexo boolean,
#   edad integer,
#   ocupacion character varying,
#   estado_civil character varying,
#   nombre character varying,
#   fecha_nacimiento date,
#   antecedentes_familiares character varying,
#   antecedentes_personales character varying,
#   antecedentes_clinicos character varying,
#   facultad character varying,
#   CONSTRAINT cedula_paciente PRIMARY KEY (cedula )
# )"""
#
#     crear_cita = """CREATE TABLE cita
# (
#   fecha date NOT NULL,
#   paciente character varying NOT NULL,
#   asistencia boolean,
#   caso_nuevo boolean,
#   asuntos_tratados character varying,
#   responsable character varying,
#   descripcion character varying,
#   beck_ansiedad character varying,
#   beck_depresion character varying,
#   cuestionarios_pendientes character varying,
#   CONSTRAINT id_cita PRIMARY KEY (paciente , fecha ),
#   CONSTRAINT cita_fk_paciente FOREIGN KEY (paciente)
#       REFERENCES paciente (cedula) MATCH SIMPLE
#       ON UPDATE NO ACTION ON DELETE NO ACTION
# )"""
#
#     insertar_paciente = """INSERT INTO paciente(
#             cedula, sexo, edad, ocupacion, estado_civil, nombre, fecha_nacimiento,
#             antecedentes_familiares, antecedentes_personales, antecedentes_clinicos,
#             facultad)
#     VALUES ("123456789", False, 24, "Estudiante", "Casado", "Juan Granda", "1997-12-26",
#             "Familia monoparental, vive con su madre con la que refiere mantener muy buenas relaciones, su  hermana mayor reside en  la ciudad de Loja por motivos de estudio.", ""El paciente se caracteriza por ser muy comunicativo, le gusta manipular las cosas y tiene una actitud colaboradora Jonathan se muestra tranquilo y obediente, La relación con su madre es buena ya que la madre tiene mas contacto con el niño, Su  padre en ocasiones agrede verbalmente a Jonathan y su contacto con el niño es escaso, Por lo cual la relación con el padre no es la adecuada, Jonathan tiene una  buena relación con su hermana menor ya que juega y mira Televisión con ella."",
#             "Sufre de trastorno bipolar. Dos intentos de suicidio.",
#             "Ingeniería");"""
#     insertar_cita = """INSERT INTO cita(
#             fecha, paciente, asistencia, caso_nuevo, asuntos_tratados, responsable,
#             descripcion, beck_ansiedad, beck_depresion, cuestionarios_pendientes)
#     VALUES (?, ?, ?, ?, ?, ?,
#             ?, ?, ?, ?);
# """
#     try:
#         conn = connect2(r"./bienestar.db")
#         cur = conn.cursor()
#         cur.execute(crear_paciente)
#         cur.execute(crear_cita)
#         cur.execute(insertar_paciente)
#         # cur.execute(insertar_cita)
#         conn.commit()
#         conn.close()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#     finally:
#         if conn is not None:
#             conn.close()
#             print('Database connection closed.')
#
#
# try:
#     conn = connect2(r"./bienestar.db")
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM paciente")
#     paciente=cur.fetchall()
#     print(paciente)
#     conn.commit()
#     conn.close()
# except (Exception, psycopg2.DatabaseError) as error:
#     print(error)
# finally:
#     if conn is not None:
#         conn.close()
#         print('Database connection closed.')