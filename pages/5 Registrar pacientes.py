import datetime
import streamlit as st
from utilidades.otros import limpiar, logo_titulo


logo_titulo()


def registrar_paciente(base):
    with base:
        mensaje = "Error en el registro"
        with st.form("registro", clear_on_submit=True):
            cedula = st.text_input("Cédula", help="Cualquier documento de identificación es permitido en caso de personas extranjeras")
            nombres = st.text_input("Nombres")
            apellidos = st.text_input("Apellidos")
            nombre_preferido = st.text_input("Nombre preferido")
            genero = st.text_input("Género")
            fecha_nacimiento = st.date_input(
                "Fecha de nacimiento (Año/Mes/Día)", min_value=datetime.date(1900, 1, 1)
            )
            ocupacion = st.text_input("Ocupación")
            correo_electronico = st.text_input("Correo electrónico")
            estado_civil = st.selectbox(
                "Estado civil",
                ("Soltero", "Casado", "Divorciado", "Viudo", "Union de hecho"),
            )
            rol = estado_civil = st.selectbox(
                "Rol que cumple dentro de la universidad",
                ("Estudiante", "Personal administrativo", "Otro"),
            )
            facultad = st.text_input("Facultad/Dependencia", help="Facultad para estudiantes, docentes, personal administrativo. Dependencia para otros trabajaores.")
            carrera = st.text_input("Carrera", help="Unicamente en caso de ser estudiante")
            ciudad_nacimiento = st.text_input("Ciudad de nacimiento")
            ciudad_residencia = st.text_input("Ciudad de residencia")
            direccion = st.text_input("Dirección del domicilio")
            hijos = st.number_input("Número de hijos", min_value=0)
            personas_vive = st.text_input(
                "Personas con las que vive",
                placeholder="Ingrese las personas separadas con una coma.",
            )
            contacto_emergencia_nombre = st.text_input(
                "Nombre del contacto de emergencia"
            )
            contacto_emergencia_parentezco = st.text_input(
                "Parentezco del contacto de emergencia",
                help="Por ejemplo: Padre, Madre, Hermano",
            )
            contacto_emergencia_telefono = st.text_input(
                "Teléfono del contacto de emergencia"
            )
            antecendentes_familiares = st.text_area("Antecedentes familiares", help="Ejemplo: Información clínica pertinente, relaciones personales con familiares.")
            antecendentes_personales = st.text_area("Antecedentes personales", help="Información clínica relevante del paciente")
            antecendentes_clinicos = st.text_area("Información adicional", help="Espacio para cualquier otro tipo de información")
            submit = st.form_submit_button("Registrar")
            if submit:
                try:
                    mensaje = "Paciente registrado"
                except:
                    mensaje = "Paciente registrado"
                    print("Error al registrar usuario")
                return mensaje


limpiar("Registro de pacientes")

registro = st.tabs(["Registrar paciente"])

base = st.empty()
mensaje = registrar_paciente(base)

if mensaje == "Paciente registrado":
    base.empty()
    st.success(mensaje)
    st.button("Aceptar")
if mensaje == "El paciente ya se encuentra registrado":
    base.empty()
    st.error(mensaje)
    st.button("Aceptar")
