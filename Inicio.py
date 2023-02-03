import pandas as pd
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from utilidades.otros import limpiar, logo_titulo

logo_titulo()

if "registrar_cita" not in st.session_state:
    st.session_state.registrar_cita = False

if "sesion_seleccionada" not in st.session_state:
    st.session_state.sesion_seleccionada = " "

limpiar("Citas del día de hoy")

historial = [
    ["10:00", "Juan Idrovo"],
    ["11:00", "Sofia Segarra"],
    ["12:00", "Juan Cardenas"],
    ["13:00", "Camila Quito"],
    ["14:00", "Damian Yapa"],
]

tabla = pd.DataFrame(historial, columns=["Hora", "Paciente"], index=None)
# builder = GridOptionsBuilder.from_dataframe(tabla)
#
# builder.configure_selection(selection_mode='single', use_checkbox=True)
# gridoptions = builder.build()
# #
# sesion = AgGrid(tabla, gridOptions=gridoptions, fit_columns_on_grid_load=True, enable_enterprise_modules=False)
# #
# sesion_seleccionada = sesion["selected_rows"]


# nombre="jaime"
# if sesion_seleccionada:
#     st.subheader("Información de la cita")
#     st.write(f"Tareas enviadas: ")
#     col1, col2, col3, col4, col5 = st.columns(5, gap="small")
#     col1.button("Iniciar sesión", type="primary", key="in" + nombre.replace(" ", ""))
#     col2.button("Ver paciente", key="ver" + nombre)
#     col3.button("Reagendar", key="rea" + nombre)
#     col4.button("No asistió", key="falta" + nombre)
#     col5.button("Cancelar", key="can" + nombre)

# if sesion_seleccionada:
#     st.stop()

lista_personas = []

tabla = tabla.values.tolist()

for cita in tabla:
    hora = cita[0]
    nombre = cita[1]
    label = ":red[" + hora + "]" + " " + nombre
    label = f"**{hora}** {nombre}"
    with st.expander(label=label):
        st.write("Tareas previas:")
        st.write("Ejercicios de respiración. Lista de actividades.")

        # iniciar, ver, reagendar, ausentismo, cancelar = st.columns(5)
        # with iniciar:
        #     st.button("Iniciar sesión",type="primary", key=label+"iniciar")
        # with ver:
        #     st.button("Ver paciente", type="secondary", key=label+"ver")
        # with reagendar:
        #     st.button("Reagendar cita", key=label+"reagendar")
        # with ausentismo:
        #     st.button("Marcar ausentismo", key=label+"ausentismo")
        # with cancelar:
        #     st.button("Cancelar cita", key=label+"cancelar")

        # page = st_btn_select(
        #     # The different pages
        #     ('Iniciar sesión', 'Ver paciente', 'Reagendar cita', 'Marcar ausentismo', 'Cancelar cita'),
        #
        #     # You can pass a formatting function. Here we capitalize the options
        #     format_func=lambda name: name.capitalize(),
        #     key=label,
        # )
        col1, col2, col3, col4, col5 = st.columns(5, gap="small")
        col1.button(
            "Iniciar sesión", type="primary", key="in" + nombre.replace(" ", "")
        )
        col2.button("Ver paciente", key="ver" + nombre)
        col3.button("Reagendar", key="rea" + nombre)
        col4.button("No asistió", key="falta" + nombre)
        col5.button("Cancelar", key="can" + nombre)
        lista_personas.append("in" + nombre.replace(" ", ""))

for persona in lista_personas:
    if st.session_state[persona] == True:
        st.session_state.pagina = "Historial"
        st.session_state.cedula = "123456789"
        st.session_state.sesion_seleccionada = 0
        switch_page("Información pacientes")
        break

# hasta aqui
