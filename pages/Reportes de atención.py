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


# def show_appointment_metrics_fullfilled(month,year):
#     colored_header(label="Citas por atención", color_name="red-50", description="")
#     appointment_list = get_appointment_report(
#         st.session_state.db_engine, get_month_number(month), int(year)
#     )
#     if appointment_list:
#         df_appointment_list = pd.DataFrame(
#             [(a.appointment_type, a.status, a.reason) for a in appointment_list],
#             columns=["Tipo de cita", "Estado", "Razón"],
#         )
#         appointment_counts = df_appointment_list["Estado"].value_counts()
#         try:
#             citas_efectivas = appointment_counts["atendida"]
#             citas_no_efectivas = appointment_counts["no_atendida"]
#             cola, colb, colc = st.columns(3)
#             cola.metric("Citas agendadas", citas_efectivas + citas_no_efectivas)
#             colb.metric("Citas efectivas", citas_efectivas)
#             colc.metric("Citas no efectivas", citas_no_efectivas)
#         except:
#             st.write("No existen suficientes datos del mes para generar el reporte")


def show_appointment_metrics_fullfilled(month, year):
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
            fig, ax = plt.subplots()
            ax.pie(
                [citas_efectivas, citas_no_efectivas],
                labels=["Citas efectivas", "Citas no efectivas"],
                autopct="%1.1f%%",
            )
            ax.set_title("Porcentaje de citas por atención")
            st.pyplot(fig)
        except:
            st.write("No existen suficientes datos del mes para generar el reporte")


# def show_appointment_metrics_type(month,year):
#     colored_header(label="Citas por tipo", color_name="red-50", description="")
#     appointment_list = get_appointment_report(
#         st.session_state.db_engine, get_month_number(month), int(year)
#     )
#     if appointment_list:
#         df_appointment_list = pd.DataFrame(
#             [(a.appointment_type, a.status, a.reason) for a in appointment_list],
#             columns=["Tipo de cita", "Estado", "Razón"],
#         )
#         try:
#             appointment_counts = df_appointment_list["Tipo de cita"].value_counts()
#             primera_vez_count = appointment_counts["Primera vez"]
#             subsecuente_count = appointment_counts["Subsecuente"]
#
#             cola, colb, colc = st.columns(3)
#             cola.metric("Citas agendadas", primera_vez_count + subsecuente_count)
#             colb.metric("Primera vez", primera_vez_count)
#             colc.metric("Subsecuentes", subsecuente_count)
#         except:
#             st.write("No existen suficientes datos del mes para generar el reporte")
def show_appointment_metrics_type(month, year):
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
            fig, ax = plt.subplots()
            ax.pie(
                [primera_vez_count, subsecuente_count],
                labels=["Primera vez", "Subsecuentes"],
                autopct="%1.1f%%",
            )
            ax.set_title("Porcentaje de citas por tipo")
            st.pyplot(fig)
        except:
            st.write("No existen suficientes datos del mes para generar el reporte")


def show_people_sex(month, year):
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
    layout = go.Layout(title="Distribución de personas atendidas por género")
    fig = go.Figure(data=data, layout=layout)
    st.plotly_chart(fig)


def show_encounters(month, year):
    colored_header(label="Sesiones atendidas", color_name="red-50", description="")
    history_result = get_encounter_complete_history(
        st.session_state.db_engine, get_month_number(month), int(year)
    )
    cola, colb = st.columns(2)

    total_atenciones = history_result.count()
    cola.metric("Total atenciones", total_atenciones[0])
    unique_ids_count = history_result["id"].nunique()
    colb.metric("Personas atendidas", unique_ids_count)


# def show_graphs(month,year):
#     history_result = get_encounter_complete_history(
#         st.session_state.db_engine, get_month_number(month), int(year)
#     )
#     col1, col2, col3 = st.columns(3)
#     list_columns = list([col1, col2, col3])
#     counter = 0
#     list_chart_topic = history_result.keys()
#     esta = list()
#     esta.append("encounter_type")
#     esta.append("faculty_dependence")
#     esta.append("patient_type")
#     for topic in esta:
#         grouped = history_result.groupby(topic).size().reset_index(name="count")
#         with list_columns[counter]:
#             count_encounter_instances(grouped, topic)
#         if counter == 2:
#             counter = 0
#         else:
#             counter = counter + 1


def show_graphs(month, year):
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
    history_result = get_encounter_complete_history(
        st.session_state.db_engine, get_month_number(month), int(year)
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


import os

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

engine = create_engine(os.environ.get("DATABASE"))

# Appointments by type
query_appointments_by_type = """
    SELECT status, COUNT(*) as count
    FROM appointment
    GROUP BY status
"""

# Appointments by encounter type
query_appointments_by_encounter_type = """
    SELECT encounter_type, COUNT(*) as count
    FROM appointment
    GROUP BY encounter_type
"""

# Appointments by sex
query_appointments_by_sex = """
    SELECT p.sex, COUNT(*) as count
    FROM appointment a
    JOIN patient p ON a.patient_id = p.id
    GROUP BY p.sex
"""

# Appointments by faculty
query_appointments_by_faculty = """
    SELECT p.faculty_dependence, COUNT(*) as count
    FROM appointment a
    JOIN patient p ON a.patient_id = p.id
    GROUP BY p.faculty_dependence
"""

# Appointments by appointment type
query_appointments_by_appointment_type = """
    SELECT a.appointment_type, COUNT(*) as count
    FROM appointment a
    GROUP BY a.appointment_type
"""
df_appointments_by_type = pd.read_sql_query(query_appointments_by_type, engine)
df_appointments_by_encounter_type = pd.read_sql_query(
    query_appointments_by_encounter_type, engine
)
df_appointments_by_sex = pd.read_sql_query(query_appointments_by_sex, engine)
df_appointments_by_faculty = pd.read_sql_query(query_appointments_by_faculty, engine)
df_appointments_by_appointment_type = pd.read_sql_query(
    query_appointments_by_appointment_type, engine
)


def appointments_by_type_chart():
    fig, ax = plt.subplots()
    ax.bar(df_appointments_by_type["status"], df_appointments_by_type["count"])
    plt.xticks(rotation=45, ha="right")
    ax.set_title("Appointments by type")
    st.pyplot(fig)


def appointments_by_encounter_type_chart():
    fig, ax = plt.subplots()
    ax.bar(
        df_appointments_by_encounter_type["encounter_type"],
        df_appointments_by_encounter_type["count"],
    )
    plt.xticks(rotation=45, ha="right")
    ax.set_title("Appointments by encounter type")
    st.pyplot(fig)


def appointments_by_sex_chart():
    fig, ax = plt.subplots()
    ax.bar(df_appointments_by_sex["sex"], df_appointments_by_sex["count"])
    plt.xticks(rotation=45, ha="right")
    ax.set_title("Appointments by sex")
    st.pyplot(fig)


def appointments_by_faculty_chart():
    fig, ax = plt.subplots()
    ax.bar(
        df_appointments_by_faculty["faculty_dependence"],
        df_appointments_by_faculty["count"],
    )
    plt.xticks(rotation=45, ha="right")
    ax.set_title("Appointments by faculty")
    st.pyplot(fig)


def appointments_by_appointment_type_chart():
    fig, ax = plt.subplots()
    ax.bar(
        df_appointments_by_appointment_type["appointment_type"],
        df_appointments_by_appointment_type["count"],
    )
    plt.xticks(rotation=45, ha="right")
    ax.set_title("Appointments by type")
    st.pyplot(fig)


col1, col2, col3 = st.columns(3)
with col1:
    appointments_by_type_chart()
    appointments_by_sex_chart()
with col2:
    appointments_by_encounter_type_chart()
    appointments_by_appointment_type_chart()
with col3:
    appointments_by_faculty_chart()


col1, col2 = st.columns(2)
with st.sidebar:
    month = st.selectbox("Mes", options=months_list)
    year = st.selectbox("Año", options=year_list)
# show_table(month,year)
with col1:
    show_encounters(month, year)
    show_appointment_metrics_fullfilled(month, year)

with col2:
    show_appointment_metrics_type(month, year)
show_people_sex(month, year)
show_graphs(month, year)
