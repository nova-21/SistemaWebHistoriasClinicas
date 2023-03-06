import os

import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from sqlalchemy import create_engine
from streamlit_extras.colored_header import colored_header

from data.actions.appointment_actions import get_appointment_report
from data.actions.encounter_actions import get_encounter_complete_history, get_encounters_month
from utilidades.vies_utilities import clean

if "db_engine" not in st.session_state:
    st.session_state.db_engine = create_engine(os.environ.get("DATABASE"))

def get_month_number(month_name):
    months = {'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12}
    return months[month_name.lower()]


def count_encounter_instances(counts,type):
    # call the count_encounter_instances function to get the counts
    # create a horizontal bar chart using st.barchart
    st.write("Número de atenciones por ",type)
    fig, ax = plt.subplots()
    ax.barh(counts[type], counts['count'])
    ax.set_xlabel("Count")
    ax.set_ylabel("Encounter Type")
    st.pyplot(fig)

clean("Reportes mensuales y anuales")

meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']

col1,col2 = st.columns(2)
month=col1.selectbox("Mes",options=meses)

history_result = get_encounter_complete_history(st.session_state.db_engine,get_month_number(month),2023)

df_resumen = []
total_atenciones = history_result.count()
unique_ids_count = history_result['id'].nunique()

df_resumen.append(unique_ids_count)
df_resumen.append(("Total atenciones",total_atenciones[0]))

gender_counts = history_result.groupby('sex')['id'].nunique()
hombres_count = gender_counts.get('Masculino')
mujeres_count = gender_counts.get('Femenino')

st.metric("Total atenciones",total_atenciones[0])

colored_header(label="Atención por sexo", color_name="red-50", description="")



cola,colb,colc=st.columns(3)
cola.metric("Personas atendidas", unique_ids_count)
colb.metric("Mujeres",mujeres_count)
colc.metric("Hombres", hombres_count)
colored_header(label="Citas", color_name="red-50", description="")
list_appointments=get_appointment_report(st.session_state.db_engine,get_month_number(month),2023)
df = pd.DataFrame([(a.appointment_type, a.status, a.reason) for a in list_appointments],
                      columns=["Tipo de cita", "Estado", "Razón"])

appointment_counts = df["Tipo de cita"].value_counts()
primera_vez_count = appointment_counts["Primera vez"]
subsecuente_count = appointment_counts["Subsecuente"]

appointment_counts = df["Estado"].value_counts()
citas_atendidas =appointment_counts["atendida"]
citas_no_atendidas = appointment_counts["no_atendida"]


cola,colb,colc=st.columns(3)
cola.metric("Citas agendadas",citas_no_atendidas+citas_atendidas)
colb.metric("Atendidas",citas_atendidas )
colc.metric("No atendidas",citas_no_atendidas)


# filter = col2.selectbox("Filtrar",options=history_result.keys())
col1,col2, col3 = st.columns(3)
list_columns = list([col1,col2,col3])
counter=0
for topic in history_result.keys():
    grouped = history_result.groupby(topic).size().reset_index(name='count')
    with list_columns[counter]:
        count_encounter_instances(grouped, topic)

    if counter == 2:
        counter = 0
    else:
        counter = counter + 1


