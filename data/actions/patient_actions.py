import pandas as pd
from sqlalchemy import or_, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from data.create_database import Patient


def add_patient(
    db_engine,
    id,
    first_name,
    second_name,
    first_family_name,
    second_family_name,
    preferred_name,
    birth_date,
    sex,
    gender,
    sexual_orientation,
    phone_number,
    email,
    profession_occupation,
    marital_status,
    patient_type,
    faculty_dependence,
    career,
    semester,
    city_born,
    city_residence,
    address,
    children,
    lives_with,
    emergency_contact_name,
    emergency_contact_relation,
    emergency_contact_phone,
    family_history,
    personal_history,
    extra_information,
    active,
):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Create a new Patient instance
    patient = Patient(
        id=id,
        first_name=first_name,
        second_name=second_name,
        first_family_name=first_family_name,
        second_family_name=second_family_name,
        preferred_name=preferred_name,
        birth_date=birth_date,
        sex=sex,
        gender=gender,
        sexual_orientation=sexual_orientation,
        phone_number=phone_number,
        email=email,
        profession_occupation=profession_occupation,
        marital_status=marital_status,
        patient_type=patient_type,
        faculty_dependence=faculty_dependence,
        career=career,
        semester=semester,
        city_born=city_born,
        city_residence=city_residence,
        address=address,
        children=children,
        lives_with=lives_with,
        emergency_contact_name=emergency_contact_name,
        emergency_contact_relation=emergency_contact_relation,
        emergency_contact_phone=emergency_contact_phone,
        family_history=family_history,
        personal_history=personal_history,
        extra_information=extra_information,
        active=active,
    )

    try:
        # Add the new Patient to the session and commit
        session.add(patient)
        session.commit()
        return "Paciente registrado"
    except IntegrityError:
        # Rollback the session in case of IntegrityError (e.g. duplicate primary key)
        session.rollback()
        return "El paciente ya se encuentra registrado"
    finally:
        # Close the session
        session.close()


def add_patient(db_engine, patient):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        # Add the new Patient to the session and commit
        session.add(patient)
        session.commit()
        return "Paciente registrado"
    except IntegrityError:
        # Rollback the session in case of IntegrityError (e.g. duplicate primary key)
        session.rollback()
        return "El paciente ya se encuentra registrado"
    finally:
        # Close the session
        session.close()


def get_patient_search(db_engine, id_or_lastname):
    Session = sessionmaker(db_engine)
    session = Session()

    try:
        # Retrieve cedula and nombre columns from paciente table
        query = (
            session.query(
                Patient.id,
                Patient.first_name,
                Patient.second_name,
                Patient.first_family_name,
                Patient.second_family_name,
                Patient.faculty_dependence,
            )
            .filter(
                or_(
                    Patient.id == id_or_lastname,
                    func.upper(Patient.first_family_name).like(
                        func.upper(f"%{id_or_lastname}%")
                    ),
                    func.upper(Patient.second_family_name).like(
                        func.upper(f"%{id_or_lastname}%")
                    ),
                )
            )
            .all()
        )
        return query
    except SQLAlchemyError as e:
        print("Error retrieving patient data:", str(e))
        return []
    finally:
        # Close the session
        session.close()


def get_patient(db_engine, patient_id):
    Session = sessionmaker(db_engine)
    session = Session()

    try:
        # Retrieve cedula and nombre columns from paciente table
        patient = session.query(Patient).filter_by(id=patient_id).first()
        return patient
    except SQLAlchemyError as e:
        print("Error retrieving patient data:", str(e))
        return []
    finally:
        # Close the session
        session.close()

def get_all_patients(db_engine):
    Session = sessionmaker(db_engine)
    session = Session()

    try:
        patient = session.query(Patient.id,
                Patient.first_name,
                Patient.second_name,
                Patient.first_family_name,
                Patient.second_family_name,
                Patient.faculty_dependence)
        patient_df = pd.DataFrame(
            patient,
            columns=[
                "Cédula",
                "Nombre1",
                "Nombre2",
                "Apellido1",
                "Apellido2",
                "Facultad/Dependencia",
            ],
            index=None,
        ).astype(str)
        return patient_df
    except SQLAlchemyError as e:
        print("Error retrieving patient data:", str(e))
        return []
    finally:
        # Close the session
        session.close()


def update_patient(db_engine, id, fields):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Get the Patient to update
    patient = session.query(Patient).filter_by(id=id).first()

    if patient:
        # Update the Patient fields
        for field, value in fields.items():
            setattr(patient, field, value)

        # Commit the changes
        session.commit()
        print("Patient updated successfully")
    else:
        print("Error: Patient with given ID not found")

    # Close the session
    session.close()


def delete_patient(db_engine, id):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Get the Patient to deactivate
    patient = session.query(Patient).filter_by(id=id).first()

    if patient is None:
        print(f"Error: Patient with ID {id} not found")
        return

    try:
        # Deactivate the Patient by setting the 'active' field to False
        patient.active = False
        session.commit()
        print(f"Patient with ID {id} deactivated successfully")
    except:
        # Rollback the session in case of an error
        session.rollback()
        print("Error: Failed to deactivate Patient")
    finally:
        # Close the session
        session.close()
