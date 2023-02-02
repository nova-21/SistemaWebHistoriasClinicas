import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page

if "registrar_cita" not in st.session_state:
    st.session_state.registrar_cita = False

cont= st.container()
st.title("Universidad de Cuenca")
st.subheader("Dirección de Bienestar Universitario")
st.subheader("Citas del día de hoy")

historial = [["21 Enero 2023", "10:00", "Juan Idrovo"], ["21 Enero 2023", "11:00", "Sofia Segarra"], ["21 Enero 2023", "12:00", "Juan Cardenas"], ["21 Enero 2023", "13:00", "Camila Quito"], ["21 Enero 2023", "14:00", "Damian Yapa"]]

tabla = pd.DataFrame(historial, columns=["Fecha", "Hora","Paciente"], index=None)
builder = GridOptionsBuilder.from_dataframe(tabla)
builder.configure_column("Fecha", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd')

builder.configure_selection(selection_mode='single', use_checkbox=True)
gridoptions = builder.build()
#
# sesion = AgGrid(tabla, gridOptions=gridoptions, fit_columns_on_grid_load=True, enable_enterprise_modules=False)
#
# sesion_seleccionada = sesion["selected_rows"]
lista_personas=[]

tabla=tabla.values.tolist()
contador=0
for cita in tabla:
    hora = cita[1]
    nombre = cita[2]
    label = ":red[" + hora + "]" + " " + nombre
    label=f"**{hora}** {nombre}"
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
        with st.container():
            # page = st_btn_select(
            #     # The different pages
            #     ('Iniciar sesión', 'Ver paciente', 'Reagendar cita', 'Marcar ausentismo', 'Cancelar cita'),
            #
            #     # You can pass a formatting function. Here we capitalize the options
            #     format_func=lambda name: name.capitalize(),
            #     key=label,
            # )
            col1, col2, col3, col4, col5 = st.columns(5,gap="small")
            col1.button("Iniciar sesión",  type="primary", key="in"+nombre.replace(" ", ""))
            col2.button("Ver paciente",key="ver"+nombre)
            col3.button("Reagendar",key="rea"+nombre)
            col4.button("No asistió",key="falta"+nombre)
            col5.button("Cancelar",key="can"+nombre)
            lista_personas.append("in"+nombre.replace(" ", ""))

seleccionada=""
for persona in lista_personas:
    if st.session_state[persona]==True:
        seleccionada=persona
        st.session_state.pagina = "Historial"
        st.session_state.cedula = "123456789"
        st.session_state.sesion_seleccionada = ""
        switch_page("Información pacientes")



# if len(sesion_seleccionada) > 0:
#     page = st_btn_select(
#         # The different pages
#         ('Iniciar sesión', 'Ver paciente', 'Reagendar cita', 'Marcar ausentismo', 'Cancelar cita'),
#
#         # You can pass a formatting function. Here we capitalize the options
#         format_func=lambda name: name.capitalize(),
#     )
#     with st.sidebar:
#         st.button("Iniciar sesión")
#         st.button("Ver paciente")
#         st.button("Reagendar cita")
#         st.button("Marcar ausentismo")
#         st.button("Cancelar cita")


# iniciar, ver, reagendar, ausentismo, cancelar = st.columns(5)
# with iniciar:
#     st.button("Iniciar sesión")
# with ver:
#     st.button("Ver paciente")
# with reagendar:
#     st.button("Reagendar cita")
# with ausentismo:
#     st.button("Marcar ausentismo")
# with cancelar:
#     st.button("Cancelar cita")

# with st.sidebar:
#     registar=st.button("Registrar nueva cita")

# if registar:
#     st.session_state.registrar_cita = True

# if st.session_state.registrar_cita:
#     with st.form(key="cita"):
#         paciente = st.text_input("Paciente")
#         fecha = st.date_input("Fecha")
#         hora = st.time_input("Hora")
#         guardar = st.form_submit_button(label="Guardar")
#
#     if guardar:
#         st.session_state.registrar_cita = False
#         print("La cita con el paciente "+paciente+" se generó para el ", fecha, hora)
#         st.experimental_rerun()

