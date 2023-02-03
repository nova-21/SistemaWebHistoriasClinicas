import streamlit as st

from utilidades.otros import limpiar


limpiar("Registro de citas")

contenedor_form = st.empty()


with contenedor_form:
    with st.form(key="cita"):
        primera = st.radio(
            "Seleccione el tipo de cita",
            (
                "Cita regular: para pacientes registrados",
                "Primera cita: para pacientes no registrados",
            ),
        )
        paciente = st.text_input("Cédula del paciente")
        fecha = st.date_input("Fecha de la cita (Año/Mes/Día)")
        hora = st.time_input("Hora de la cita")
        guardar = st.form_submit_button(label="Guardar")

if guardar:
    st.session_state.registrar_cita = False
    contenedor_form.empty()
    st.success("La cita fue creata con éxito")
    st.button("Aceptar")
    # st.experimental_rerun()
