from datetime import date

import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, load_only

from base_de_datos.crear import Sesion, Cita, Paciente, Cuestionario, Tratante

def crear_session():
    engine = create_engine('sqlite:///base_de_datos/test.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def buscar_citas_hoy():
    session=crear_session()
    citas_hoy = pd.read_sql(session.query(Cita.hora, Cita.cedula_paciente, Paciente.nombres, Paciente.apellidos, Paciente.telefono, Paciente.facultad_dependencia, Paciente.carrera).filter_by(fecha=date.today()).join(Paciente, Paciente.cedula==Cita.cedula_paciente).statement, session.bind)
    return citas_hoy

def buscar_sesion(cedula,fecha):
    session=crear_session()
    sesion = session.query(Sesion).filter_by(cedula_paciente=cedula,fecha=fecha)
    return sesion


citas=buscar_citas_hoy()

print(citas)

