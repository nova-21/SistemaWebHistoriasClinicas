import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from data.database_declaration import Diagnostic


def update_diagnostics(db_engine, date, patient_id, diagnostics):
    """
    Update the diagnostics of a patient encounter.

    Args:
        db_engine (sqlalchemy.engine.Engine): SQLAlchemy database engine.
        date (datetime.date): Date of the encounter.
        patient_id (int): ID of the patient.
        diagnostics (list): List of diagnostics to update.

    Returns:
        None
    """
    # Create a session using the provided database engine
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        try:
            # Update the Encounter in the session and commit
            encounter = (
                session.query(Diagnostic)
                .filter(Diagnostic.patient_id == patient_id, Diagnostic.date == date)
                .first()
            )
            if encounter:
                encounter.diagnostics = ";".join(diagnostics)
                session.commit()
                print("Encounter updated successfully")
            else:
                print("Error: Encounter not found")
        finally:
            # Close the session
            session.close()


def add_diagnostic(db_engine, date, patient_id, diagnostic, type):
    """
    Add a new diagnostic for a patient encounter.

    Args:
        db_engine (sqlalchemy.engine.Engine): SQLAlchemy database engine.
        date (datetime.date): Date of the encounter.
        patient_id (int): ID of the patient.
        diagnostic (str): Diagnostic description.
        type (str): Type of diagnostic.

    Returns:
        str: Success message if the diagnostic is added successfully.
    """
    # Create a session using the provided database engine
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        try:
            # Add the new Diagnostic to the session and commit
            diag = Diagnostic(
                patient_id=patient_id, date=date, result=diagnostic, status=type
            )
            session.add(diag)
            session.commit()
            return "Diagnóstico registrado con éxito"
        except IntegrityError:
            # Rollback the session in case of IntegrityError (e.g., duplicate primary key)
            session.rollback()
            print("Error: Encounter with the same ID already exists")
        finally:
            # Close the session
            session.close()


def get_diagnostics(db_engine, patient_id, date):
    """
    Retrieve the diagnostics of a patient encounter.

    Args:
        db_engine (sqlalchemy.engine.Engine): SQLAlchemy database engine.
        patient_id (int): ID of the patient.
        date (datetime.date): Date of the encounter.

    Returns:
        pandas.DataFrame: DataFrame containing the diagnostics and their types.
    """
    # Create a session using the provided database engine
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        try:
            encounter = (
                session.query(Diagnostic.result, Diagnostic.status)
                .filter(Diagnostic.patient_id == patient_id, Diagnostic.date == date)
                .all()
            )

            if len(encounter) > 0:
                df = pd.DataFrame(
                    encounter,
                    columns=["Diagnóstico", "Tipo"],
                )
                return df
            else:
                df = pd.DataFrame(columns=["Diagnóstico", "Tipo"])
                return df
        finally:
            # Close the session
            session.close()
