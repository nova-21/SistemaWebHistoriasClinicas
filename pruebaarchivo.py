import streamlit as st
import pandas as pd

uploaded_file =st.file_uploader("Sube un cuestionario")

if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file,header=None)
    st.header("Cuestionario de "+dataframe[0][0])

    filtrados1=dataframe.loc[range(1,9,2)]

    enunciados=filtrados1[0]

    opciones=filtrados1.loc[1:,1:]

    for contador in range(0, len(enunciados)):
        opt=opciones.iloc[[contador]].dropna(axis=1).squeeze()
        enunciado=enunciados[contador:contador + 1].values[0]
        st.radio(enunciado,opt)
























