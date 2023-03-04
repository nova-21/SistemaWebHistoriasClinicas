import datetime

import pandas as pd
from sqlalchemy import cast, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from data.create_database import Encounter, Practitioner


def add_encounter(
    db_engine,
    encounter_type,
    topics_boarded,
    date,
    activities_sent,
    attachments,
    patient_id,
    practitioner_id,
):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Create a new Encounter instance
    encounter = Encounter(
        encounter_type=encounter_type,
        topics_boarded=topics_boarded,
        date=date,
        activities_sent=activities_sent,
        attachments=attachments,
        patient_id=patient_id,
        practitioner_id=practitioner_id,
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
        query = session.query(Encounter).filter(Encounter.patient_id == patient_id)
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


def update_encounter(
    db_engine,
    encounter_id,
    encounter_type,
    topics_boarded,
    date,
    activities_sent,
    attachments,
    patient_id,
    practitioner_id,
):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    try:
        # Update the Encounter in the session and commit
        encounter = (
            session.query(Encounter).filter(Encounter.id == encounter_id).first()
        )
        if encounter:
            encounter.encounter_type = encounter_type
            encounter.topics_boarded = topics_boarded
            encounter.date = date
            encounter.activities_sent = activities_sent
            encounter.attachments = attachments
            encounter.patient_id = patient_id
            encounter.practitioner_id = practitioner_id
            session.commit()
            print("Encounter updated successfully")
        else:
            print("Error: Encounter not found")
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
