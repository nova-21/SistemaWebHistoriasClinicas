import datetime
import pandas as pd
from sqlalchemy import desc, and_, extract
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from data.database_declaration import Encounter, Practitioner, Patient


def add_encounter(db_engine, encounter_type, topics_boarded, date, attachments, patient_id, practitioner_id, diagnostics):
    """
    Adds a new encounter to the database.

    Args:
        db_engine (Engine): SQLAlchemy database engine
        encounter_type (str): Type of the encounter
        topics_boarded (str): Topics boarded during the encounter
        date (datetime.datetime): Date of the encounter
        attachments (str): Attachments related to the encounter
        patient_id (int): ID of the patient
        practitioner_id (int): ID of the practitioner
        diagnostics (str): Diagnostics of the encounter

    Returns:
        str: Success message if the encounter is added successfully, or an error message if an IntegrityError occurs
    """
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        encounter = Encounter(
            encounter_type=encounter_type,
            topics_boarded=topics_boarded,
            date=date,
            attachments=attachments,
            patient_id=patient_id,
            practitioner_id=practitioner_id,
            diagnostics=diagnostics,
        )
        try:
            session.add(encounter)
            session.commit()
            return "Sesión registrada con éxito"
        except IntegrityError:
            session.rollback()
            return "Error: Sesión con el mismo ID ya existe"

def add_encounter_object(db_engine, encounter):
    """
        Adds a new encounter to the database.

        Args:
            db_engine (Engine): SQLAlchemy database engine
            encounter (Encounter): Encounter object, created with all the information

        Returns:
            str: Success message if the encounter is added successfully, or an error message if an IntegrityError occurs
        """
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    with Session() as session:

        try:
            # Add the new Encounter to the session and commit
            session.add(encounter)
            session.commit()
            return "Sesión registrada con éxito"
        except IntegrityError:
            # Rollback the session in case of IntegrityError (e.g. duplicate primary key)
            session.rollback()
            return "Error: Sesión con el mismo ID ya existe"


def get_encounter_history(db_engine, patient_id):
    """
    Retrieves the encounter history for a given patient.

    Args:
        db_engine (Engine): SQLAlchemy database engine
        patient_id (int): ID of the patient

    Returns:
        pd.DataFrame: Encounter history containing the date and encounter type for each encounter
    """
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        query = (
            session.query(Encounter)
            .filter(Encounter.patient_id == patient_id)
            .order_by(desc(Encounter.date))
        )
        encounter_history = pd.read_sql_query(query.statement, db_engine)
        encounter_history = encounter_history.loc[:, ["date", "encounter_type"]]
        encounter_history = encounter_history.rename(
            columns={"date": "Fecha", "encounter_type": "Tipo de atención"}
        )
        return encounter_history


def get_encounter_complete_history(db_engine, month, year):
    """
    Retrieves the complete encounter history for a given month and year.

    Args:
        db_engine (Engine): SQLAlchemy database engine
        month (int): Month of the encounters
        year (int): Year of the encounters

    Returns:
        pd.DataFrame: Complete encounter history containing various attributes of the encounters
    """
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        encounters = (
            session.query(
                Encounter.encounter_type,
                Patient.id,
                Patient.faculty_dependence,
                Patient.career,
                Patient.sex,
                Patient.birth_date,
                Patient.marital_status,
                Patient.patient_type,
                Patient.profession_occupation,
            )
            .join(Patient)
            .filter(
                extract("month", Encounter.date) == month,
                extract("year", Encounter.date) == year,
            )
            .all()
        )
        df = pd.DataFrame(
            encounters,
            columns=[
                "encounter_type",
                "id",
                "faculty_dependence",
                "career",
                "sex",
                "age",
                "marital_status",
                "patient_type",
                "profession_occupation",
            ],
        )
        return df


def get_encounters_month(db_engine, month, year):
    """
    Retrieves the encounters that occurred in a specific month and year.

    Args:
        db_engine (Engine): SQLAlchemy database engine
        month (int): Month of the encounters
        year (int): Year of the encounters

    Returns:
        List[Encounter]: List of encounters that occurred in the specified month and year
    """
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        encounters_in_month = (
            session.query(Encounter)
            .filter(
                and_(
                    extract("year", Encounter.date) == year,
                    extract("month", Encounter.date) == month,
                )
            )
            .all()
        )
        return encounters_in_month


def get_encounter(db_engine, patient_id, date):
    """
    Retrieves a specific encounter for a given patient and date.

    Args:
        db_engine (Engine): SQLAlchemy database engine
        patient_id (int): ID of the patient
        date (datetime.date): Date of the encounter

    Returns:
        Tuple[Encounter, str]: Tuple containing the encounter and the full name of the practitioner associated with the encounter
    """
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        encounter = (
            session.query(Encounter, Practitioner.full_name)
            .join(Practitioner, Encounter.practitioner_id == Practitioner.id)
            .filter(Encounter.patient_id == patient_id, Encounter.date == date)
            .first()
        )
        return encounter


def get_treatment(db_engine, patient_id, date):
    """
    Retrieves the treatment for a specific patient and date.

    Args:
        db_engine (Engine): SQLAlchemy database engine
        patient_id (int): ID of the patient
        date (datetime.date): Date of the encounter

    Returns:
        str: Treatment information for the specified patient and date, or an empty string if not found
    """
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        treatment = (
            session.query(Encounter.treatment)
            .filter(Encounter.patient_id == patient_id, Encounter.date == date)
            .first()
        )
        return treatment[0] if treatment and treatment[0] is not None else ""


def update_encounter(db_engine, encounter_edited):
    """
    Updates an existing encounter in the database.

    Args:
        db_engine (Engine): SQLAlchemy database engine
        encounter_edited (Encounter): Edited encounter object to update

    Raises:
        Exception: If an error occurs during the update process
    """
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        try:
            session.add(encounter_edited)
            session.commit()
        except Exception as e:
            raise e


def update_treatment(db_engine, treatment, patient_id, date):
    """
    Updates the treatment for a specific patient and date.

    Args:
        db_engine (Engine): SQLAlchemy database engine
        treatment (str): New treatment information
        patient_id (int): ID of the patient
        date (datetime.date): Date of the encounter
    """
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        encounter = (
            session.query(Encounter)
            .filter(Encounter.patient_id == patient_id, Encounter.date == date)
            .first()
        )
        if encounter:
            if encounter.treatment != treatment:
                encounter.treatment = treatment
                session.commit()
                print("Encounter updated successfully")
            else:
                print("No changes")
        else:
            print("Error: Encounter not found")


def update_eval(
    db_engine,
    motive,
    evolution_notes,
    actual_demand_illness,
    psychological_evaluation,
    patient_id,
    date,
):
    """
    Updates the evaluation information for a specific patient and date.

    Args:
        db_engine (Engine): SQLAlchemy database engine
        motive (str): Updated motive for the encounter
        evolution_notes (str): Updated evolution notes for the encounter
        actual_demand_illness (str): Updated actual demand illness for the encounter
        psychological_evaluation (str): Updated psychological evaluation for the encounter
        patient_id (int): ID of the patient
        date (datetime.date): Date of the encounter
    """
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        encounter = (
            session.query(Encounter)
            .filter(Encounter.patient_id == patient_id, Encounter.date == date)
            .first()
        )
        if encounter:
            if motive != encounter.motive:
                encounter.motive = motive
            if evolution_notes != encounter.evolution_notes:
                encounter.evolution_notes = evolution_notes
            if actual_demand_illness != encounter.actual_demand_illness:
                encounter.actual_demand_illness = actual_demand_illness
            if psychological_evaluation != encounter.psychological_evaluation:
                encounter.psychological_evaluation = psychological_evaluation

            if session.dirty:
                session.commit()
                print("Encounter updated successfully")
            else:
                print("No changes")
        else:
            print("Error: Encounter not found")


def update_attachment(db_engine, patient_id, date, attachments):
    """
    Updates the attachments for a specific patient and date.

    Args:
        db_engine (Engine): SQLAlchemy database engine
        patient_id (int): ID of the patient
        date (datetime.date): Date of the encounter
        attachments (str): Updated attachments information
    """
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        encounter = (
            session.query(Encounter)
            .filter(Encounter.patient_id == patient_id, Encounter.date == date)
            .first()
        )
        if encounter:
            if not encounter.attachments:
                encounter.attachments = attachments
            else:
                encounter.attachments += ";" + attachments
            session.commit()
            print("Encounter updated successfully")
        else:
            print("Error: Encounter not found")


def get_attachments_list(db_engine, patient_id, date):
    """
    Retrieves the list of attachments for a specific patient and date.

    Args:
        db_engine (Engine): SQLAlchemy database engine
        patient_id (int): ID of the patient
        date (datetime.date): Date of the encounter

    Returns:
        List[str]: List of attachments for the specified patient and date
    """
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        attachments = (
            session.query(Encounter.attachments)
            .filter(Encounter.patient_id == patient_id, Encounter.date == date)
            .first()
        )
        return attachments[0].split(";") if attachments and attachments[0] else []


def delete_encounter(db_engine, encounter_id):
    """
    Deletes an encounter from the database.

    Args:
        db_engine (Engine): SQLAlchemy database engine
        encounter_id (int): ID of the encounter to delete
    """
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        encounter = (
            session.query(Encounter).filter(Encounter.id == encounter_id).first()
        )
        if encounter:
            session.delete(encounter)
            session.commit()
            print("Encounter deleted successfully")
        else:
            print("Error: Encounter not found")
