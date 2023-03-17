import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid
import streamlit as st

with st.sidebar:
    contenedor_tabla = st.empty()


with contenedor_tabla.container():
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
    with st.form(key="form_historial"):
        sesion = AgGrid(
            tabla,
            gridOptions=gridoptions,
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=False,
        )
        st.form_submit_button("Aceptar")
    sesion_seleccionada = sesion["selected_rows"]

sesion_seleccionada

st.subheader("haesdflkj")
dsf = st.button("adsf")
