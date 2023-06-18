import os
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool


def create_engine_conection():
    """
    Create a SQLAlchemy engine connection to the database.
    """
    db_engine = create_engine(os.environ.get("DATABASE"), poolclass=NullPool)
    return db_engine
