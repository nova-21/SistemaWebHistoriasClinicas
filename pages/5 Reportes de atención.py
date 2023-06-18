import os
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt, font_manager
from sqlalchemy import create_engine
from streamlit_elements import dashboard
from st_aggrid import GridOptionsBuilder, AgGrid
from streamlit_extras.colored_header import colored_header
from streamlit_elements import elements, mui, html
from data.repositories.AppointmentRepository import get_appointment_report
from data.repositories.EncounterRepository import (
    get_encounter_complete_history,
    get_encounters_month,
)
from data.database_connection import create_engine_conection
from utilities.view_utilities import clean
import matplotlib.pyplot as plt

if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine_conection()

st.set_page_config(layout="wide")

months_list = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]

year_list = ["2023", "2022", "2021"]
title_dict = {
    "encounter_type": "Tipo de atención",
    "faculty_dependence": "Facultad/Dependencia",
    "patient_type": "Tipo de paciente",
}

def get_month_number(month_name):
    """
    Convert month name to month number.

    Args:
        month_name (str): Name of the month in Spanish.

    Returns:
        int: Corresponding month number.
    """
    months_dict = {
        "enero": 1,
        "febrero": 2,
        "marzo": 3,
        "abril": 4,
        "mayo": 5,
        "junio": 6,
        "julio": 7,
        "agosto": 8,
        "septiembre": 9,
        "octubre": 10,
        "noviembre": 11,
        "diciembre": 12,
    }
    return months_dict[month_name.lower()]


def count_encounter_instances(counts, type_column):
    """
    Count encounter instances and create a horizontal bar chart.

    Args:
        counts (pd.DataFrame): DataFrame containing counts of encounter instances.
        type_column (str): Column name representing the type of encounter.

    Returns:
        None
    """
    title = title_dict[type_column.lower()]
    st.write(title)
    fig, ax = plt.subplots()
    ax.barh(counts[type_column], counts["count"])
    ax.set_xlabel("Count")
    ax.set_ylabel("Encounter Type")
    st.pyplot(fig)


clean("Reportes mensuales y anuales")


def show_appointment_metrics_fullfilled(month, year):
    """
    Show appointment metrics based on fulfillment status.

    Args:
        month (str): Selected month.
        year (str): Selected year.

    Returns:
        None
    """
    colored_header(label="Citas por atención", color_name="red-50", description="")
    appointment_list = get_appointment_report(
        st.session_state.db_engine, get_month_number(month), int(year)
    )
    if appointment_list:
        df_appointment_list = pd.DataFrame(
            [(a.appointment_type, a.status, a.reason) for a in appointment_list],
            columns=["Tipo de cita", "Estado", "Razón"],
        )
        appointment_counts = df_appointment_list["Estado"].value_counts()
        try:
            citas_efectivas = appointment_counts["atendida"]
            citas_no_efectivas = appointment_counts["no_atendida"]
            fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
            ax.pie(
                [citas_efectivas, citas_no_efectivas],
                labels=["Citas efectivas", "Citas no efectivas"],
                autopct="%1.1f%%",
                textprops={'fontsize': 9}
            )
            st.pyplot(fig)
        except:
            st.write("No existen suficientes datos del mes para generar el reporte")


def show_appointment_metrics_type(month, year):
    """
    Show appointment metrics based on appointment type.

    Args:
        month (str): Selected month.
        year (str): Selected year.

    Returns:
        None
    """
    colored_header(label="Citas por tipo", color_name="red-50", description="")
    appointment_list = get_appointment_report(
        st.session_state.db_engine, get_month_number(month), int(year)
    )
    if appointment_list:
        df_appointment_list = pd.DataFrame(
            [(a.appointment_type, a.status, a.reason) for a in appointment_list],
            columns=["Tipo de cita", "Estado", "Razón"],
        )
        try:
            appointment_counts = df_appointment_list["Tipo de cita"].value_counts()
            primera_vez_count = appointment_counts["Primera vez"]
            subsecuente_count = appointment_counts["Subsecuente"]
            fig, ax = plt.subplots(figsize=(2, 2), dpi=300)
            ax.pie(
                [primera_vez_count, subsecuente_count],
                labels=["Primera vez", "Subsecuentes"],
                autopct="%1.1f%%",
                textprops={'fontsize': 8}
            )
            st.pyplot(fig)
        except:
            st.write("No existen suficientes datos del mes para generar el reporte")


def show_people_sex(month, year):
    """
    Show gender distribution of people attended.

    Args:
        month (str): Selected month.
        year (str): Selected year.

    Returns:
        None
    """
    import plotly.graph_objs as go

    colored_header(label="Personas atendidas", color_name="red-50", description="")
    history_result = get_encounter_complete_history(
        st.session_state.db_engine, get_month_number(month), int(year)
    )
    gender_counts = history_result.groupby("sex")["id"].nunique()
    unique_ids_count = history_result["id"].nunique()
    hombres_count = gender_counts.get("Masculino")
    mujeres_count = gender_counts.get("Femenino")
    cola, colb = st.columns(2)
    cola.metric("Mujeres", mujeres_count)
    colb.metric("Hombres", hombres_count)

    # Create a vertical bar chart
    data = [
        go.Bar(
            x=["Mujeres", "Hombres"],
            y=[mujeres_count, hombres_count],
            marker=dict(color=["pink", "blue"]),
            text=[
                f"{mujeres_count} ({mujeres_count/unique_ids_count:.1%})",
                f"{hombres_count} ({hombres_count/unique_ids_count:.1%})",
            ],
            textposition="auto",
            orientation="v",
        )
    ]


def show_encounters(month, year):
    """
    Show number of encounters and unique individuals attended.

    Args:
        month (str): Selected month.
        year (str): Selected year.

    Returns:
        None
    """
    colored_header(label="Sesiones atendidas", color_name="red-50", description="")
    history_result = get_encounter_complete_history(
        st.session_state.db_engine, get_month_number(month), int(year)
    )
    cola, colb = st.columns(2)

    total_atenciones = history_result.count()
    cola.metric("Total atenciones", total_atenciones[0])
    unique_ids_count = history_result["id"].nunique()
    colb.metric("Personas atendidas", unique_ids_count)


def show_graphs(month, year):
    """
    Show graphs based on encounter topics.

    Args:
        month (str): Selected month.
        year (str): Selected year.

    Returns:
        None
    """
    history_result = get_encounter_complete_history(
        st.session_state.db_engine, get_month_number(month), int(year)
    )
    col1, col2, col3 = st.columns(3)
    list_columns = list([col1, col2, col3])
    counter = 0
    list_chart_topic = history_result.keys()
    esta = list()
    esta.append("encounter_type")
    esta.append("faculty_dependence")
    esta.append("patient_type")
    for topic in esta:
        grouped = history_result.groupby(topic).size().reset_index(name="count")
        top_4 = grouped.nlargest(4, "count")
        with list_columns[counter]:
            st.write(f"**Número de instancias de encuentros por {topic}**")
            st.dataframe(top_4, height=200)
        if counter == 2:
            counter = 0
        else:
            counter = counter + 1


def show_table(month, year):
    """
    Show table with encounter details.

    Args:
        month (str): Selected month.
        year (str): Selected year.

    Returns:
        None
    """
    history_result = get_encounter_complete_history(
        st.session_state.db_engine, get_month_number(month), int(year)
    )
    builder = GridOptionsBuilder.from_dataframe(history_result)
    builder.configure_auto_height(True)
    builder.configure_selection(selection_mode="single", use_checkbox=False)
    builder.configure_side_bar(defaultToolPanel=True)
    builder.configure_default_column(
        groupable=True,
        sorteable=True,
        enableRowGroup=True,
        enablePivot=True,
        enableValue=True,
        allowedAggFuncs=["sum", "avg", "count", "min", "max"],
    )
    gridoptions = builder.build()
    with elements("dashboard"):
        sesion = AgGrid(
            history_result,
            gridOptions=gridoptions,
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=True,
        )


col1, col2 = st.columns(2)
with st.sidebar:
    month = st.selectbox("Mes", options=months_list)
    year = st.selectbox("Año", options=year_list)
# show_table(month,year)
with col1:
    show_encounters(month, year)
    show_appointment_metrics_fullfilled(month, year)

with col2:
    show_people_sex(month, year)
    show_appointment_metrics_type(month, year)

show_graphs(month, year)
