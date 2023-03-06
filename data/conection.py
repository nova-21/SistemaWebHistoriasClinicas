import os
from sqlalchemy import create_engine
import streamlit as st

def create_engine_conection():
    db_engine = create_engine(st.secrets("DATABASE"))
    return db_engine