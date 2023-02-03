from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from crear import Tratante, Sesion, Paciente, Cita

engine = create_engine('sqlite:///test.db')

Session = sessionmaker(bind=engine)
session = Session()

tratante1 = Tratante(cedula="1234567890", nombre_completo="Juan Carlos Davalos Cuenca", posicion="Psicologo clinico", correo_institucional="juan.davalos@ucuenca.edu.ec", telefono="0994834336")
paciente1 = Paciente(
    cedula="0106785215", nombres = "Alex David", apellidos = "Pinos Palacios", nombre_preferido = "", email = "", fecha_nacimiento =date.today(),
    ciudad_nacimiento = "", ciudad_residencia = "", direccion = "",telefono="", genero = "", ocupacion="",
    estado_civil="", vive_con="", hijos="", rol_universitario="", contacto_emergencia_nombre="",
    contacto_emergencia_telefono="", contacto_emergencia_parentezco="", antecedentes_familiares="", antecedentes_personales="",
    informacion_extra="", facultad_dependencia="", carrera=""
                     )
cita1 = Cita(cedula_paciente="0106785215",fecha=date.today(), hora="10:00", primera_cita=True, tratante_id="1234567890")
sesion1 = Sesion(cedula_paciente="0106785215", fecha=date.today(), primera_sesion=False, razon_consulta="Test", tratante_id="1234567890", tareas="ninguna", archivos_adjuntos="Nada")

session.add(tratante1)
session.add(paciente1)
session.add(cita1)
session.add(sesion1)

session.commit()