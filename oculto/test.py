import pandas as pd
import streamlit as st
from st_aggrid import GridOptionsBuilder, AgGrid
from streamlit_extras.colored_header import colored_header
import time
from utilidades.vies_utilities import clean
from streamlit_extras.switch_page_button import switch_page

clean("Búsqueda de pacientes")

# Definición de contadores
contenedor_busqueda = st.empty()
contenedor_resultados = st.empty()
contenedor_datos_personales = st.empty()


with st.sidebar:
    contenedor_controles = st.empty()

# Definicion de variables de estado
if "vista_actual" not in st.session_state:
    st.session_state.vista_actual = "busqueda"

if "controles_editar" not in st.session_state:
    st.session_state.controles_editar = False


def buscar_datos_personales(valor_busqueda):
    return [("123456789", "Alex Pinos"), ("987654321", "Jaime Quito")]
    # return ([])


def cambiar_a_vista_perfil():
    contenedor_busqueda.empty()
    contenedor_resultados.empty()
    st.session_state.vista_actual = "perfil"
    st.experimental_rerun()


def cambiar_a_vista_inicio():
    st.session_state.current_view = "busqueda"


def vista_busqueda():
    with contenedor_busqueda:
        valor_busqueda = st.text_input(
            "Ingrese la cédula o los apellidos del paciente para la búsqueda"
        )
        if valor_busqueda != "":
            resultado_busqueda = buscar_datos_personales(valor_busqueda)
            with contenedor_resultados.container():
                if len(resultado_busqueda) == 0:
                    st.warning(
                        "No existen resultados. ¿Deseas registrar un nuevo paciente?"
                    )
                    registrar = st.button("Registrar nuevo paciente")
                    if registrar:
                        switch_page("Registrar pacientes")
                else:
                    resultados_dataframe = pd.DataFrame(
                        resultado_busqueda, columns=["Cédula", "Nombre"], index=None
                    )
                    print(resultados_dataframe)
                    colms = st.columns((1, 2, 2))
                    fields = ["Cédula", "Nombre"]
                    for col, field_name in zip(colms, fields):
                        col.write(field_name)
                    for x, email in enumerate(resultados_dataframe["Cédula"]):
                        col1, col2, col3 = st.columns((1, 2, 2))
                        col1.write(
                            resultados_dataframe["Cédula"][x]
                        )  # cedula identidad
                        col2.write(resultados_dataframe["Nombre"][x])  # nombre completo
                        button_phold = col3.empty()  # create a placeholder
                        do_action = button_phold.button("Seleccionar", key=x)
                        if do_action:
                            cambiar_a_vista_perfil()
                            # resultados_dataframe['Cédula'][x]
                            break


@st.cache
def get_data():
    return [
        ("2022-12-12", "Test"),
        ("2022-12-12", "Test"),
        ("2022-12-12", "Test"),
        ("2022-12-12", "Test"),
    ]


@st.cache_data
def get_table():
    historial = [
        ("2022-12-12", "Test"),
        ("2022-12-12", "Test"),
        ("2022-12-12", "Test"),
        ("2022-12-12", "Test"),
    ]
    tabla = pd.DataFrame(historial, columns=["Fecha", "Descripción corta"], index=None)
    tabla["Descripción corta"].fillna("", inplace=True)
    builder = GridOptionsBuilder.from_dataframe(tabla)
    builder.configure_column(
        "Fecha", type=["customDateTimeFormat"], custom_format_string="yyyy-MM-dd"
    )
    builder.configure_selection(selection_mode="single", use_checkbox=True)
    gridoptions = builder.build()
    return tabla, gridoptions


def vista_perfil():
    tabla, gridoptions = get_table()
    with contenedor_datos_personales.container():
        colored_header(label="Datos personales", color_name="red-50", description="")
        with st.expander("Datos personales"):
            col1, col2 = st.columns([1, 1])

            editar_datos = st.button("Editar", key="editar_datos")
            editar_datos = False
            if not editar_datos:
                with col1:
                    st.write("Cédula: ")
                    st.write("Género: ")
                    st.write("Fecha de nacimiento: ")
                    st.write("E-mail: ")
                    st.write("Facultad de dependencia: ")
                    st.write("Contacto de emergencia: ")
                    st.write("Parentezco: ")
                    st.write("Personas con las que vive: ")

                with col2:
                    st.write("Nombre preferido: ")
                    st.write("Ocupación: ")
                    st.write("Estado civil: ")
                    st.write("Ciudad de nacimiento: ")
                    st.write("Ciudad de residencia: ")
                    st.write("Hijos: ")
                    st.write("Dirección:")

            else:
                # with col1:
                #     with st.form(key="editar datos"):
                #         st.text_input("Este")
                #         st.form_submit_button("Guardar")
                print("Hi")

        with st.expander("Antecedentes personales"):
            st.write("Lorem ipsum")
        with st.expander("Antecedentes familiares"):
            st.write("Lorem ipsum")
        with st.expander("Otra información"):
            st.write("Lorem ipsum")

    # with contenedor_controles.container():

    with st.sidebar:
        colored_header(label="Controles", color_name="red-50", description="")
        st.button(
            "🏠 Regresar a la búsqueda de pacientes",
            type="primary",
            key="dos",
            on_click=cambiar_a_vista_inicio,
        )
        if st.session_state.controles_editar == []:
            st.button("Editar")
        colored_header(
            label="Historial de sesiones", color_name="red-50", description=""
        )
        st.write("Seleccione la sesión que desea visualizar")

        sesion = AgGrid(
            tabla,
            gridOptions=gridoptions,
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=False,
        )

        sesion_seleccionada = sesion["selected_rows"]
        st.session_state.controles_editar = sesion_seleccionada


if st.session_state.vista_actual == "perfil":
    vista_perfil()

if st.session_state.vista_actual == "busqueda":
    vista_busqueda()
