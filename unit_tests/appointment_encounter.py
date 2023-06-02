import os
import random
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from data.conection import create_engine_conection
from data.create_database import Appointment, Encounter, Patient, Practitioner
from utilidades.lists import list_encounter_types


def generate_random_date(days_ago):
    today = datetime.datetime.today()
    past_date = today - datetime.timedelta(days=random.randint(1, days_ago))
    return past_date.strftime("%Y-%m-%d")


def test_insert_appointments():
    engine = create_engine_conection()
    Session = sessionmaker(engine)
    db_session = Session()
    patient_ids = db_session.query(Patient.id).all()
    practitioner_ids = db_session.query(Practitioner.id).all()

    for i in range(500):
        # Generate a random date between 1 and 365 days ago
        days_ago = random.randint(1, 365)
        random_date = datetime.datetime.today() - datetime.timedelta(days=days_ago)
        appointment_date = datetime.datetime(
            random_date.year, random_date.month, random_date.day
        )
        e_t = random.choice(list_encounter_types)
        appointment = Appointment(
            status="atendida",
            date=appointment_date,
            patient_id=random.choice(patient_ids)[0],
            appointment_type=random.choice(["Primera vez", "Subsecuente"]),
            encounter_type=e_t,
            practitioner_id=random.choice(practitioner_ids)[0],
        )
        encounter = Encounter(
            date=appointment_date,
            patient_id=appointment.patient_id,
            encounter_type=e_t,
            practitioner_id=appointment.practitioner_id,
        )
        db_session.add(appointment)
        db_session.add(encounter)
    db_session.commit()


def test_insert_appointments_subsecuentes():
    engine = create_engine_conection()
    Session = sessionmaker(engine)
    db_session = Session()
    patient_ids = db_session.query(Patient.id).all()
    practitioner_ids = db_session.query(Practitioner.id).all()

    for i in range(100):
        # Generate a random date between 1 and 365 days ago
        days_ago = random.randint(1, 365)
        random_date = datetime.datetime.today() - datetime.timedelta(days=days_ago)
        appointment_date = datetime.datetime(
            random_date.year, random_date.month, random_date.day
        )
        e_t = random.choice(list_encounter_types)
        appointment = Appointment(
            status="no_atendida",
            date=appointment_date,
            patient_id=random.choice(patient_ids)[0],
            appointment_type=random.choice(["Primera vez", "Subsecuente"]),
            encounter_type=e_t,
            practitioner_id=random.choice(practitioner_ids)[0],
            reason = random.choice(["Ausentismo","Reagendamiento por el paciente",
                        "Reagendamiento por el tratante",])
        )
        db_session.add(appointment)

    db_session.commit()

test_insert_appointments()
test_insert_appointments_subsecuentes()
