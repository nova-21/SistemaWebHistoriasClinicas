import os
from sqlalchemy import create_engine
import streamlit as st
from sqlalchemy.pool import NullPool


def create_engine_conection():
    db_engine = create_engine(os.environ.get("DATABASE"), poolclass=NullPool)
    return db_engine
