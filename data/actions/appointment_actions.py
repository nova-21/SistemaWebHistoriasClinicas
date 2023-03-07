import datetime
from sqlite3 import IntegrityError

import pandas as pd
from sqlalchemy import cast, String, desc, asc, and_, extract, func
from sqlalchemy.orm import sessionmaker

from data.create_database import Appointment, Patient, Practitioner, Encounter


def add_appointment(
    db_engine, patient_id, practitioner_id, appointment_type, status, reason, date, time
):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Create a new Appointment instance
    appointment = Appointment()
    appointment.appointment_type = appointment_type
    appointment.status = status
    appointment.reason = reason
    appointment.patient_id = patient_id
    appointment.practitioner_id = practitioner_id
    appointment.date = date
    appointment.time = time

    try:
        # Add the new Appointment to the session and commit
        session.add(appointment)
        session.commit()
        return "Cita registrada con éxito"
    except IntegrityError:
        # Rollback the session in case of IntegrityError (e.g. duplicate primary key)
        session.rollback()
        message = (
            "Error con el registro de la cita, revise los datos e intente nuevamente."
        )
        print(message)
        return message
    finally:
        # Close the session
        session.close()


def get_todays_appointments(engine):
    # create the session
    Session = sessionmaker(bind=engine)
    session = Session()
    from datetime import datetime, timedelta
    import pytz

    timezone = pytz.timezone('US/Eastern')
    utc_time = datetime.utcnow()
    local_time = utc_time + timedelta(hours=-5)
    local_time = timezone.localize(local_time)

    # format the date as Y-M-D
    today_str = local_time.strftime('%Y-%m-%d')

    # query the appointments and join with the related patient and practitioner
    appointments = (
        session.query(
            Appointment.time,
            Patient.id,
            Patient.first_name,
            Patient.first_family_name,
            Patient.faculty_dependence,
            Patient.career,
            Patient.phone_number,
        )
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(Practitioner, Appointment.practitioner_id == Practitioner.id)
        .filter(cast(Appointment.date, String) == today_str).order_by(asc(Appointment.time))
        .all()
    )

    # create a dataframe from the query results
    # citas_hoy = pd.read_sql(session.query(Cita.hora, Cita.cedula_paciente, Paciente.nombres, Paciente.apellidos, Paciente.telefono, Paciente.facultad_dependencia, Paciente.carrera).filter_by(fecha=date.today()).join(Paciente, Paciente.cedula==Cita.cedula_paciente).statement, session.bind)

    df = pd.DataFrame(
        appointments,
        columns=[
            "Hora",
            "Cédula",
            "Nombre",
            "Apellido",
            "Facultad/Dependencia",
            "Carrera",
            "Teléfono",
        ],
    )
    # close the session
    session.close()

    return df

def get_appointment_report(engine,month,year):
    # create the session
    Session = sessionmaker(bind=engine)
    session = Session()

    appointments = session.query(Appointment).filter(
            func.strftime('%m', Appointment.date) == f'{month:02}',
            func.strftime('%Y', Appointment.date) == str(year)
        ).all()


    # close the session
    session.close()

    return appointments

def get_appointment(engine,patient_id,date):
    # create the session
    Session = sessionmaker(bind=engine)
    session = Session()

    # get today's date as a string in the format YYYY-MM-DD
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    # query the appointments and join with the related patient and practitioner
    appointments = (
        session.query(
            Appointment.time,
            Patient.id,
            Patient.first_name,
            Patient.first_family_name,
            Patient.faculty_dependence,
            Patient.career,
            Patient.phone_number,
        )
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(Practitioner, Appointment.practitioner_id == Practitioner.id)
        .filter(cast(Appointment.date, String) == today_str)
        .all()
    )

    # create a dataframe from the query results
    # citas_hoy = pd.read_sql(session.query(Cita.hora, Cita.cedula_paciente, Paciente.nombres, Paciente.apellidos, Paciente.telefono, Paciente.facultad_dependencia, Paciente.carrera).filter_by(fecha=date.today()).join(Paciente, Paciente.cedula==Cita.cedula_paciente).statement, session.bind)

    df = pd.DataFrame(
        appointments,
        columns=[
            "Hora",
            "Cédula",
            "Nombre",
            "Apellido",
            "Facultad/Dependencia",
            "Carrera",
            "Teléfono",
        ],
    )
    # close the session
    session.close()

    return df



def update_appointment(
    db_engine,
    appointment_id,
    appointment_type,
    status,
    reason,
    date,
    time,
    patient_id,
    practitioner_id,
):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    try:
        # Update the Appointment in the session and commit
        appointment = (
            session.query(Appointment).filter(Appointment.id == appointment_id).first()
        )
        if appointment:
            appointment.appointment_type = appointment_type
            appointment.status = status
            appointment.reason = reason
            appointment.date = date
            appointment.time = time
            appointment.patient_id = patient_id
            appointment.practitioner_id = practitioner_id
            session.commit()
            print("Appointment updated successfully")
        else:
            print("Error: Appointment not found")
    finally:
        # Close the session
        session.close()


def delete_appointment(db_engine, appointment_id):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    try:
        # Delete the Appointment from the session and commit
        appointment = (
            session.query(Appointment).filter(Appointment.id == appointment_id).first()
        )
        if appointment:
            session.delete(appointment)
            session.commit()
            print("Appointment deleted successfully")
        else:
            print("Error: Appointment not found")
    finally:
        # Close the session
        session.close()
