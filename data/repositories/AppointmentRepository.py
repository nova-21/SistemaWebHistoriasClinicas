from datetime import datetime
from sqlite3 import IntegrityError
import pandas as pd
from sqlalchemy import cast, String, desc, asc, and_, extract
from sqlalchemy.orm import sessionmaker
from data.repositories.PatientRepository import get_patient
from data.database_declaration import Appointment, Patient, Practitioner, Encounter


def add_appointment(
        db_engine,
        patient_id,
        practitioner_id,
        appointment_type,
        encounter_type,
        status,
        reason,
        date,
        time,
):
    """Add a new appointment to the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): Database engine.
        patient_id (int): Patient ID.
        practitioner_id (int): Practitioner ID.
        appointment_type (str): Appointment type.
        encounter_type (str): Encounter type.
        status (str): Appointment status.
        reason (str): Reason for the appointment.
        date (datetime.date): Appointment date.
        time (datetime.time): Appointment time.

    Returns:
        str: Success or error message.
    """
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
    appointment.encounter_type = encounter_type

    try:
        res = get_appointment(db_engine, patient_id, date)

        if res is not None:
            raise Exception(
                "El paciente ya cuenta con una cita en esa fecha, seleccione una distinta."
            )
        # Add the new Appointment to the session and commit
        patient_search = get_patient(db_engine, patient_id)

        if patient_search is None:
            raise Exception("El paciente no se encuentra registrado")
        session.add(appointment)
        session.commit()
        return "Cita registrada con éxito"
    except IntegrityError:
        # Rollback the session in case of IntegrityError (e.g. duplicate primary key)
        session.rollback()
        message = (
            "Error con el registro de la cita, revise los datos e intente nuevamente."
        )
        return message
    except Exception as e:
        session.rollback()
        return str(e)
    finally:
        # Close the session
        session.close()


def get_todays_appointments(engine, practitioner_id):
    """Get today's appointments for a specific practitioner.

    Args:
        engine (sqlalchemy.engine.Engine): Database engine.
        practitioner_id (int): Practitioner ID.

    Returns:
        pandas.DataFrame: DataFrame containing appointment information.
    """
    # create the session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Get current time in the specified timezone
    from datetime import datetime, timedelta
    import pytz

    timezone = pytz.timezone("US/Eastern")
    utc_time = datetime.utcnow()
    local_time = utc_time + timedelta(hours=-5)
    local_time = timezone.localize(local_time)

    # format the date as Y-M-D
    today_str = local_time.strftime("%Y-%m-%d")

    # query the appointments and join with the related patient and practitioner
    appointments = (
        session.query(
            Appointment.time,
            Appointment.encounter_type,
            Patient.id,
            Patient.first_name,
            Patient.first_family_name,
            Patient.faculty_dependence,
            Patient.career,
            Patient.phone_number,
        )
            .join(Patient, Appointment.patient_id == Patient.id)
            .join(Practitioner, Appointment.practitioner_id == Practitioner.id)
            .filter(
            cast(Appointment.date, String) == today_str,
            Appointment.status == "booked",
            Practitioner.id == practitioner_id
        )
            .order_by(asc(Appointment.time))
            .all()
    )

    # create a dataframe from the query results
    df = pd.DataFrame(
        appointments,
        columns=[
            "Hora",
            "Tipo de atención",
            "Cédula",
            "Nombre",
            "Apellido",
            "Dependencia",
            "Carrera",
            "Teléfono",
        ],
    )

    # add a new column called "Nombre completo" by joining "first_name" and "first_family_name"
    df["Paciente"] = df["Nombre"] + " " + df["Apellido"]
    # drop the "Nombre" and "Apellido" columns
    df.drop(columns=["Nombre", "Apellido"], inplace=True)
    # move the "Nombre completo" column to the fourth position
    cols = df.columns.tolist()
    cols.insert(3, cols.pop(cols.index("Paciente")))
    df = df.reindex(columns=cols)

    # close the session
    session.close()

    return df


def get_appointment_report(engine, month, year):
    """Get appointment report for a specific month and year.

    Args:
        engine (sqlalchemy.engine.Engine): Database engine.
        month (int): Month.
        year (int): Year.

    Returns:
        list: List of Appointment objects.
    """
    # create the session
    Session = sessionmaker(bind=engine)
    session = Session()

    start_date = datetime(year=year, month=month, day=1)
    end_date = (
        datetime(year=year, month=month + 1, day=1)
        if month < 12
        else datetime(year=year + 1, month=1, day=1)
    )
    appointments = (
        session.query(Appointment)
            .filter(and_(Appointment.date >= start_date, Appointment.date < end_date))
            .all()
    )

    # close the session
    session.close()

    return appointments


def get_appointment(engine, patient_id, date):
    """Get appointment for a specific patient and date.

    Args:
        engine (sqlalchemy.engine.Engine): Database engine.
        patient_id (int): Patient ID.
        date (datetime.date): Appointment date.

    Returns:
        tuple: Tuple containing appointment information.
    """
    # create the session
    Session = sessionmaker(bind=engine)
    session = Session()
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
            .filter(
            cast(Appointment.date, String) == cast(date, String),
            Patient.id == patient_id,
        )
            .first()
    )

    # close the session
    session.close()
    return appointments


def update_appointment(
        db_engine,
        status,
        reason,
        date,
        patient_id,
):
    """Update an appointment in the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): Database engine.
        status (str): Appointment status.
        reason (str): Reason for the appointment.
        date (datetime.date): Appointment date.
        patient_id (int): Patient ID.
    """
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    try:
        # Update the Appointment in the session and commit
        appointment = (
            session.query(Appointment)
                .filter(Appointment.date == date, Appointment.patient_id == patient_id)
                .first()
        )

        if appointment:
            appointment.status = status
            appointment.reason = reason
            session.commit()
            print("Appointment updated successfully")
        else:
            print("Error: Appointment not found")
    finally:
        # Close the session
        session.close()


def delete_appointment(db_engine, appointment_id):
    """Delete an appointment from the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): Database engine.
        appointment_id (int): Appointment ID.
    """
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
