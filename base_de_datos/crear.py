from datetime import date

from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

engine = create_engine('sqlite:///test.db')

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class Paciente(Base):
    __tablename__ = 'paciente'
    cedula = Column(String(10), primary_key=True)
    nombres = Column(String(50))
    apellidos = Column(Integer)
    nombre_preferido = Column(String(50))
    email = Column(String(50))
    fecha_nacimiento = Column(Date)
    ciudad_nacimiento = Column(String(25))
    ciudad_residencia = Column(String(25))
    telefono = Column(String(11))
    direccion = Column(String(50))
    sexo = Column(String(50))
    genero = Column(String(20))
    ocupacion = Column(String(20))
    estado_civil = Column(String(20))
    vive_con = Column(String(30))
    hijos = Column(Integer)
    rol_universitario = Column(String(20))
    contacto_emergencia_nombre = Column(String(20))
    contacto_emergencia_telefono = Column(String(10))
    contacto_emergencia_parentezco = Column(String(20))
    antecedentes_familiares = Column(String())
    antecedentes_personales = Column(String())
    informacion_extra = Column(String())
    facultad_dependencia = Column(String(20))
    carrera = Column(String(20))
    sesion = relationship("Sesion", back_populates="paciente")
    cita = relationship("Cita", back_populates="paciente")

class Tratante(Base):
    __tablename__ = 'tratante'
    cedula = Column(String(10), primary_key=True)
    nombre_completo = Column(String(50))
    posicion = Column(String(20))
    correo_institucional = Column(String(50))
    telefono = Column(String(10))
    cita = relationship('Cita', back_populates='tratante')
    sesion = relationship('Sesion', back_populates='tratante')

class Sesion(Base):
    __tablename__ = 'sesion'
    id = Column(Integer, primary_key=True)
    cedula_paciente = Column(String(10), ForeignKey('paciente.cedula'))
    paciente = relationship("Paciente", back_populates="sesion")
    fecha = Column(Date)
    primera_sesion = Column(Boolean)
    razon_consulta = Column(String(50))
    tareas = Column(String(50))
    archivos_adjuntos = Column(String(50))
    tratante_id = Column(String(50), ForeignKey('tratante.cedula'))
    tratante = relationship("Tratante", back_populates="sesion")


class Cita(Base):
    __tablename__ = 'cita'
    id = Column(Integer, primary_key=True)
    cedula_paciente = Column(String(10) , ForeignKey('paciente.cedula'))
    paciente = relationship("Paciente",back_populates="cita")
    fecha = Column(Date)
    hora = Column(String(5))
    primera_cita = Column(Boolean)
    tratante_id = Column(String(50), ForeignKey('tratante.cedula'))
    tratante = relationship("Tratante",back_populates="cita")

class Cuestionario(Base):
    __tablename__ = 'cuestionario'
    cedula = Column(String(10), primary_key=True)
    fecha = Column(Date, primary_key=True)
    nombre = Column(String(20))
    resultado = Column(Integer)
    respuestas = Column(String())

Base.metadata.create_all(engine)