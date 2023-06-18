import pandas as pd
from sqlalchemy import or_, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from data.database_declaration import Patient, Appointment, Encounter, Diagnostic, QuestionnaireResponse


def add_patient(db_engine, id, first_name, second_name, first_family_name, second_family_name,
                preferred_name, birth_date, sex, gender, sexual_orientation, phone_number,
                email, profession_occupation, marital_status, patient_type, faculty_dependence,
                career, semester, city_born, city_residence, address, children, lives_with,
                emergency_contact_name, emergency_contact_relation, emergency_contact_phone,
                family_history, personal_history, habits, extra_information, active):
    """
    Add a new patient to the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): The database engine.
        id (str): The patient ID.
        first_name (str): The first name of the patient.
        second_name (str): The second name of the patient.
        first_family_name (str): The first family name of the patient.
        second_family_name (str): The second family name of the patient.
        preferred_name (str): The preferred name of the patient.
        birth_date (datetime.date): The birth date of the patient.
        sex (str): The sex of the patient.
        gender (str): The gender of the patient.
        sexual_orientation (str): The sexual orientation of the patient.
        phone_number (str): The phone number of the patient.
        email (str): The email address of the patient.
        profession_occupation (str): The profession or occupation of the patient.
        marital_status (str): The marital status of the patient.
        patient_type (str): The type of patient.
        faculty_dependence (str): The faculty or dependence of the patient.
        career (str): The career of the patient.
        semester (int): The semester of the patient.
        city_born (str): The city where the patient was born.
        city_residence (str): The city of residence of the patient.
        address (str): The address of the patient.
        children (int): The number of children of the patient.
        lives_with (str): Information about who the patient lives with.
        emergency_contact_name (str): The name of the emergency contact person.
        emergency_contact_relation (str): The relation to the emergency contact person.
        emergency_contact_phone (str): The phone number of the emergency contact person.
        family_history (str): The family history of the patient.
        personal_history (str): The personal history of the patient.
        habits (str): The habits of the patient.
        extra_information (str): Any extra information about the patient.
        active (bool): The active status of the patient.

    Returns:
        str: A message indicating the result of the operation.
    """
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
        habits=habits,
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


def add_patient_object(db_engine, patient):
    """
    Add a new patient to the database using a Patient object.

    Args:
        db_engine (sqlalchemy.engine.Engine): The database engine.
        patient (Patient): The Patient object representing the patient to add.

    Returns:
        str: A message indicating the result of the operation.
    """
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()
    try:
        # Add the new Patient to the session and commit
        session.add(patient)
        session.commit()
        return "Paciente registrado con éxito"
    except IntegrityError:
        # Rollback the session in case of IntegrityError (e.g. duplicate primary key)
        session.rollback()
        return "El paciente ya se encuentra registrado"
    finally:
        # Close the session
        session.close()


def get_patient_search(db_engine, id_or_lastname):
    """
    Search for patients in the database based on the ID or last name.

    Args:
        db_engine (sqlalchemy.engine.Engine): The database engine.
        id_or_lastname (str): The ID or last name to search for.

    Returns:
        list: A list of tuples containing the patient data matching the search criteria.
    """
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
    """
    Get a patient from the database based on the ID.

    Args:
        db_engine (sqlalchemy.engine.Engine): The database engine.
        patient_id (str): The ID of the patient to retrieve.

    Returns:
        Patient: The Patient object representing the retrieved patient.
    """
    Session = sessionmaker(db_engine)
    session = Session()

    try:
        # Retrieve cedula and nombre columns from paciente table
        patient = session.query(Patient).filter_by(id=patient_id).first()
        print(patient)
        return patient
    except SQLAlchemyError as e:
        print("Error retrieving patient data:", str(e))
        return []
    finally:
        # Close the session
        session.close()


def get_all_patients(db_engine):
    """
    Get all patients from the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): The database engine.

    Returns:
        pandas.DataFrame: A DataFrame containing all the patient data.
    """
    Session = sessionmaker(db_engine)
    session = Session()

    try:
        patient = session.query(
            Patient.id,
            Patient.first_name,
            Patient.second_name,
            Patient.first_family_name,
            Patient.second_family_name,
            Patient.faculty_dependence,
        )
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
    """
    Update a patient's information in the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): The database engine.
        id (str): The ID of the patient to update.
        fields (dict): A dictionary containing the fields to update and their new values.

    Returns:
        None
    """
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


def deactivate_patient(db_engine, id):
    """
    Deactivate a patient in the database by setting the 'active' field to False.

    Args:
        db_engine (sqlalchemy.engine.Engine): The database engine.
        id (str): The ID of the patient to deactivate.

    Returns:
        None
    """
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


def delete_patient(db_engine, id):
    """
    Delete a patient from the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): The database engine.
        id (str): The ID of the patient to delete.

    Returns:
        None
    """
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Get the Patient to delete
    patient = session.query(Patient).filter_by(id=id).first()

    if patient is None:
        print(f"Error: Patient with ID {id} not found")
        return

    try:
        # Delete the associated records in other tables
        session.query(Diagnostic).filter_by(patient_id=id).delete()
        session.query(Appointment).filter_by(patient_id=id).delete()
        session.query(Encounter).filter_by(patient_id=id).delete()
        session.query(QuestionnaireResponse).filter_by(patient_id=id).delete()

        # Delete the Patient
        session.delete(patient)
        session.commit()
        print(f"Patient with ID {id} deleted successfully")
    except:
        # Rollback the session in case of an error
        session.rollback()
        print("Error: Failed to delete Patient")
    finally:
        # Close the session
        session.close()
