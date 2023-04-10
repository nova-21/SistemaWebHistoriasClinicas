import os

import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from sqlalchemy import create_engine
from streamlit_elements import dashboard
from st_aggrid import GridOptionsBuilder, AgGrid
from streamlit_extras.colored_header import colored_header
from streamlit_elements import elements, mui, html
from data.actions.appointment_actions import get_appointment_report
from data.actions.encounter_actions import (
    get_encounter_complete_history,
    get_encounters_month,
)
from data.conection import create_engine_conection
from utilidades.vies_utilities import clean

if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine_conection()

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
title_dict = {
    "encounter_type": "Tipo de atención",
    "faculty_dependence": "Facultad/Dependencia",
    "patient_type": "Tipo de paciente",
}


def get_month_number(month_name):
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
    # call the count_encounter_instances function to get the counts
    # create a horizontal bar chart using st.barchart
    title = title_dict[type_column.lower()]
    st.write(title)
    fig, ax = plt.subplots()
    ax.barh(counts[type_column], counts["count"])
    ax.set_xlabel("Count")
    ax.set_ylabel("Encounter Type")
    st.pyplot(fig)


clean("Reportes mensuales y anuales")


def show_appointment_metrics_fullfilled(month):
    colored_header(label="Citas por atención", color_name="red-50", description="")
    appointment_list = get_appointment_report(
        st.session_state.db_engine, get_month_number(month), 2023
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
            cola, colb, colc = st.columns(3)
            cola.metric("Citas agendadas", citas_efectivas + citas_no_efectivas)
            colb.metric("Citas efectivas", citas_efectivas)
            colc.metric("Citas no efectivas", citas_no_efectivas)
        except:
            st.write("No existen suficientes datos del mes para generar el reporte")


def show_appointment_metrics_type(month):
    colored_header(label="Citas por tipo", color_name="red-50", description="")
    appointment_list = get_appointment_report(
        st.session_state.db_engine, get_month_number(month), 2023
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

            cola, colb, colc = st.columns(3)
            cola.metric("Citas agendadas", primera_vez_count + subsecuente_count)
            colb.metric("Primera vez", primera_vez_count)
            colc.metric("Subsecuentes", subsecuente_count)
        except:
            st.write("No existen suficientes datos del mes para generar el reporte")

def show_people_sex(month):
    colored_header(label="Personas atendidas", color_name="red-50", description="")
    history_result = get_encounter_complete_history(
        st.session_state.db_engine, get_month_number(month), 2023
    )
    gender_counts = history_result.groupby("sex")["id"].nunique()
    unique_ids_count = history_result["id"].nunique()
    hombres_count = gender_counts.get("Masculino")
    mujeres_count = gender_counts.get("Femenino")
    cola, colb, colc = st.columns(3)
    cola.metric("Personas atendidas", unique_ids_count)
    colb.metric("Mujeres", mujeres_count)
    colc.metric("Hombres", hombres_count)


def show_encounters(month):
    colored_header(label="Sesiones atendidas", color_name="red-50", description="")
    history_result = get_encounter_complete_history(
        st.session_state.db_engine, get_month_number(month), 2023
    )
    total_atenciones = history_result.count()
    st.metric("Total atenciones", total_atenciones[0])


def show_graphs(month):
    history_result = get_encounter_complete_history(
        st.session_state.db_engine, get_month_number(month), 2023
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
        with list_columns[counter]:
            count_encounter_instances(grouped, topic)
        if counter == 2:
            counter = 0
        else:
            counter = counter + 1


def show_table(month):
    history_result = get_encounter_complete_history(
        st.session_state.db_engine, get_month_number(month), 2023
    )
    # df_appointment_list = pd.DataFrame([(a.encounter_type, a.id, a.faculty_dependence, a.career, a.sex, a.age,a.marital_status, a.patient_type, a.profession_occupation) for a in history_result],
    #                                    columns=["Tipo de atención", "Cédula", "Facultad/Dependencia","Carrera","Sexo","Edad","Estado civil","Tipo de paciente","Ocupación"])

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
show_table(month)
show_appointment_metrics_fullfilled(month)
show_appointment_metrics_type(month)
show_people_sex(month)
show_encounters(month)
show_graphs(month)
