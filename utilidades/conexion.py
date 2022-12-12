import psycopg2
import streamlit
import sqlite3
from sqlite3 import Error

# def connect(db_file):
#     conn = sqlite3.connect(db_file)
#     return conn

def connect():
    conn = psycopg2.connect(
        host="localhost",
        database="bienestar",
        user="postgres",
        password="admin")
    return conn

def buscar_datos_personales(datos_personales):
    conn = None
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

def buscar_datos_personales2(cedula):
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        query = "SELECT paciente.cedula, paciente.nombre,fecha_nacimiento, ocupacion, estado_civil, facultad, antecedentes_familiares, antecedentes_personales, antecedentes_clinicos FROM paciente WHERE cedula='{0}'".format(
            cedula)
        cur.execute(query)
        resultado_busqueda = cur.fetchone()
        print(resultado_busqueda)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
        return resultado_busqueda


def buscar_historial(cedula):
    conn = None
    historial=""
    try:
        conn = connect()
        cur = conn.cursor()

        query = "SELECT to_char(fecha, 'YYYY-MM-DD') as date,descripcion from cita where paciente='{0}' order by date desc".format(
            cedula)
        cur.execute(query, cedula)
        historial = cur.fetchall()
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
        return historial


def buscar_sesion(cedula,fecha):
    conn = connect()
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

def registrar_sesion_db(lista_datos):
    ##TODO conexion a la base de datos
    print("exito")

def guardar_archivos(archivos):
    ##TODO crear funcion para serializar archivos en disco
    print("Exito")


def restore():

    data=connect(r"./bienestar.db")

