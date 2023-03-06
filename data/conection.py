import os
from sqlalchemy import create_engine

def create_engine_conection():
    db_engine = create_engine(os.environ.get("DATABASE"))
    return db_engine