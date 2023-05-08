import datetime

import pandas as pd
from sqlalchemy import cast, String, desc, and_, extract
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from data.create_database import Encounter, Practitioner, Patient, Diagnostic


def add_encounter(
    db_engine,
    encounter_type,
    topics_boarded,
    date,
    attachments,
    patient_id,
    practitioner_id,
    diagnostics,
):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Create a new Encounter instance
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
        # Add the new Encounter to the session and commit
        session.add(encounter)
        session.commit()
        print("New Encounter added successfully")
    except IntegrityError:
        # Rollback the session in case of IntegrityError (e.g. duplicate primary key)
        session.rollback()
        print("Error: Encounter with the same ID already exists")
    finally:
        # Close the session
        session.close()


def add_encounter(db_engine, encounter):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    try:
        # Add the new Encounter to the session and commit
        session.add(encounter)
        session.commit()
        return "Sesión registrada con éxito"
    except IntegrityError:
        # Rollback the session in case of IntegrityError (e.g. duplicate primary key)
        session.rollback()
        print("Error: Encounter with the same ID already exists")
    finally:
        # Close the session
        session.close()


def get_encounter_history(db_engine, patient_id):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        query = (
            session.query(Encounter)
            .filter(Encounter.patient_id == patient_id)
            .order_by(desc(Encounter.date))
        )
        encounter_history = pd.read_sql_query(query.statement, db_engine)
        # select and order desired columns
        encounter_history = encounter_history.loc[:, ["date", "encounter_type"]]
        # rename columns
        encounter_history = encounter_history.rename(
            columns={"date": "Fecha", "encounter_type": "Tipo de atención"}
        )
        return encounter_history
    finally:
        # Close the session
        session.close()


def get_encounter_complete_history(db_engine, month, year):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    try:
        # retrieve encounters of a particular type that occurred within the specified month and year
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

        # convert the results into a pandas DataFrame
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
    finally:
        # Close the session
        session.close()


def get_encounters_month(db_engine, month, year):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
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
    finally:
        # Close the session
        session.close()


def get_encounter(db_engine, patient_id, date):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        encounter = (
            session.query(Encounter, Practitioner.full_name)
            .join(Practitioner, Encounter.practitioner_id == Practitioner.id)
            .filter(Encounter.patient_id == patient_id, Encounter.date == date)
            .first()
        )

        return encounter
    finally:
        # Close the session

        session.close()


def get_treatment(db_engine, patient_id, date):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        treatment = (
            session.query(Encounter.treatment)
            .filter(Encounter.patient_id == patient_id, Encounter.date == date)
            .first()
        )
        if treatment[0] == None:
            return ""
        else:
            return treatment[0]
    finally:
        # Close the session

        session.close()


# def update_encounter(
#     db_engine,
#     encounter_id,
#     encounter_type,
#     topics_boarded,
#     date,
#     activities_sent,
#     attachments,
#     patient_id,
#     practitioner_id,
# ):
#     # Create a Session
#     Session = sessionmaker(bind=db_engine)
#     session = Session()
#
#     try:
#         # Update the Encounter in the session and commit
#         encounter = (
#             session.query(Encounter)
#             .filter(Encounter.patient_id == patient_id, Encounter.date == date)
#             .first()
#         )
#         if encounter:
#             encounter.encounter_type = encounter_type
#             encounter.topics_boarded = topics_boarded
#             encounter.date = date
#             encounter.activities_sent = activities_sent
#             encounter.attachments = attachments
#             encounter.patient_id = patient_id
#             encounter.practitioner_id = practitioner_id
#             session.commit()
#             print("Encounter updated successfully")
#         else:
#             print("Error: Encounter not found")
#     finally:
#         # Close the session
#         session.close()


def update_encounter(db_engine, encounter_edited):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    try:
        session.add(encounter_edited)
        session.commit()
    except Exception as e:
        raise e
    finally:
        # Close the session
        session.close()

def update_treatment(db_engine, treatment, patient_id, date):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    try:
        # Update the Encounter with a new attachment, in the session and commit
        encounter = (
            session.query(Encounter)
                .filter(Encounter.patient_id == patient_id, Encounter.date == date)
                .first()
        )

        if encounter:
            if (
                    encounter.treatment != treatment
            ):  # Inserts the new attachment path separated by ; if it's not empty
                encounter.treatment = treatment
                session.commit()
            else:
                print("No changes")
            print("Encounter updated successfully")
        else:
            print("Error: Encounter not found")
    finally:
        # Close the session
        session.close()

def update_eval(db_engine, motive, evolution_notes, actual_demand_illness, psychological_evaluation, patient_id, date):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    try:
        # Update the Encounter with new information, in the session and commit
        encounter = (
            session.query(Encounter)
                .filter(Encounter.patient_id == patient_id, Encounter.date == date)
                .first()
        )

        if encounter:
            # Compare each submit parameter with the corresponding Encounter attribute
            if motive != encounter.motive:
                encounter.motive = motive
            if evolution_notes != encounter.evolution_notes:
                encounter.evolution_notes = evolution_notes
            if actual_demand_illness != encounter.actual_demand_illness:
                encounter.actual_demand_illness = actual_demand_illness
            if psychological_evaluation != encounter.psychological_evaluation:
                encounter.psychological_evaluation = psychological_evaluation

            # Commit changes if any of the submit parameters differ from the Encounter attributes
            if session.dirty:
                session.commit()
                print("Encounter updated successfully")
            else:
                print("No changes")
        else:
            print("Error: Encounter not found")
    finally:
        # Close the session
        session.close()



def update_attachment(db_engine, patient_id, date, attachments):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    try:
        # Update the Encounter with a new attachment, in the session and commit
        encounter = (
            session.query(Encounter)
            .filter(Encounter.patient_id == patient_id, Encounter.date == date)
            .first()
        )

        if encounter:
            if (
                not encounter.attachments
            ):  # Inserts the new attachment path separated by ; if it's not empty
                encounter.attachments = attachments
            else:
                encounter.attachments += ";" + attachments
            session.commit()
            print("Encounter updated successfully")
        else:
            print("Error: Encounter not found")
    finally:
        # Close the session
        session.close()


def get_attachments_list(db_engine, patient_id, date):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    try:
        # Get list of the attachments paths
        attachments = (
            session.query(Encounter.attachments)
            .filter(Encounter.patient_id == patient_id, Encounter.date == date)
            .first()
        )
        if attachments[0] is not None:
            return attachments[0].split(";")
        else:
            return list()
    finally:
        # Close the session
        session.close()


def delete_encounter(db_engine, encounter_id):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    try:
        # Delete the Encounter from the session and commit
        encounter = (
            session.query(Encounter).filter(Encounter.id == encounter_id).first()
        )
        if encounter:
            session.delete(encounter)
            session.commit()
            print("Encounter deleted successfully")
        else:
            print("Error: Encounter not found")
    finally:
        # Close the session
        session.close()
