import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid
from streamlit_extras.switch_page_button import switch_page

from base_de_datos.read import buscar_citas_hoy
from utilidades.otros import limpiar, logo_titulo

logo_titulo()

if "registrar_cita" not in st.session_state:
    st.session_state.registrar_cita = False

if "sesion_seleccionada" not in st.session_state:
    st.session_state.sesion_seleccionada = " "

limpiar("Citas del día de hoy")

historial=buscar_citas_hoy()

#     print(cita.tratante.nombre_completo, cita.primera_cita)
# historial = [
#     ["10:00", "Juan Idrovo"],
#     ["11:00", "Sofia Segarra"],
#     ["12:00", "Juan Cardenas"],
#     ["13:00", "Camila Quito"],
#     ["14:00", "Damian Yapa"],
# ]
tabla=historial[['hora','cedula_paciente','nombres','apellidos','telefono']]

# tabla = pd.DataFrame(historial, columns=["Hora", "Cédula", "Nombres", "Apellidos"], index=None)
builder = GridOptionsBuilder.from_dataframe(tabla)

builder.configure_selection(selection_mode='single', use_checkbox=False)
gridoptions = builder.build()
#
sesion = AgGrid(tabla, gridOptions=gridoptions, fit_columns_on_grid_load=True, enable_enterprise_modules=False)
#
sesion_seleccionada = sesion["selected_rows"]


nombre="jaime"
if sesion_seleccionada:
    st.subheader("Información de la cita")
    st.write(f"**Tareas enviadas:** ")
    st.write("Ejercicios de respiración. Realizar una lista de actividades.")
    col1, col2, col3, col4, col5 = st.columns(5, gap="small")
    col1.button("Iniciar sesión", type="primary", key="in" + nombre.replace(" ", ""))
    col2.button("Ver paciente", key="ver" + nombre)
    col3.button("Reagendar", key="rea" + nombre)
    col4.button("No asistió", key="falta" + nombre)
    col5.button("Cancelar", key="can" + nombre)

if sesion_seleccionada:
    st.stop()

lista_personas = []

tabla = tabla.values.tolist()

for cita in tabla:
    hora = cita[0]
    print(cita[0],cita[2],cita[3])
    nombre = cita[2] + " " +cita[3]
    # label = ":red[" + str(hora) + "]" + " " + nombre
    label = f"**{hora}** {nombre}"
    with st.expander(label=label):
        st.markdown("###### Tareas enviadas en la sesión anterior:")
        st.write("Ejercicios de respiración. Realizar una lista de actividades.")
        st.markdown(" **Teléfono:** "+ cita[4])

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
