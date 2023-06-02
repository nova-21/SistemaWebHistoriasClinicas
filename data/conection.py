import os
from sqlalchemy import create_engine
import streamlit as st
from sqlalchemy.pool import NullPool


def create_engine_conection():
    db_engine = create_engine("postgresql://postgres:Pe#ogqXi6E57h^@database-2.cm0w6xqlv87w.us-east-2.rds.amazonaws.com:5432", poolclass=NullPool)
    return db_engine
