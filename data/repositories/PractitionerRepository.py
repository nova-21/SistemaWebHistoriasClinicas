from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from data.database_declaration import Practitioner

def add_practitioner(db_engine, practitioner_id, full_name, position, email, phone_number, active):
    """
    Add a new practitioner to the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): SQLAlchemy database engine.
        practitioner_id (int): Practitioner ID.
        full_name (str): Full name of the practitioner.
        position (str): Position of the practitioner.
        email (str): Email address of the practitioner.
        phone_number (str): Phone number of the practitioner.
        active (bool): Flag indicating if the practitioner is active.

    Returns:
        None
    """
    # Create a session using the provided database engine
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        # Create a new Practitioner instance
        practitioner = Practitioner(
            id=practitioner_id,
            full_name=full_name,
            position=position,
            email=email,
            phone_number=phone_number,
            active=active,
        )
        try:
            # Add the new Practitioner to the session and commit the changes
            session.add(practitioner)
            session.commit()
            print("New Practitioner added successfully")
        except IntegrityError:
            # Rollback the session in case of IntegrityError (e.g., duplicate primary key)
            session.rollback()
            print("Error: Practitioner with the same ID already exists")

def get_practitioners(db_engine):
    """
    Retrieve a list of active practitioners from the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): SQLAlchemy database engine.

    Returns:
        list: List of tuples containing practitioner information (full name, email, ID, position).
    """
    # Create a session using the provided database engine
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        try:
            # Retrieve active practitioners' full name, email, ID, and position
            practitioners = session.query(
                Practitioner.full_name,
                Practitioner.email,
                Practitioner.id,
                Practitioner.position
            ).filter(Practitioner.active == True).all()
            return practitioners
        except Exception as e:
            print("Error retrieving practitioner data:", str(e))
            return []

def get_practitioner_by_email(db_engine, email):
    """
    Retrieve a practitioner's ID based on the email.

    Args:
        db_engine (sqlalchemy.engine.Engine): SQLAlchemy database engine.
        email (str): Email address of the practitioner.

    Returns:
        int: Practitioner ID, or None if not found.
    """
    # Create a session using the provided database engine
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        try:
            # Retrieve the practitioner's ID based on the email
            practitioner = session.query(Practitioner.id).filter_by(email=email).first()
            return practitioner
        except Exception as e:
            print("Error retrieving practitioner data:", str(e))
            return None

def update_practitioner(db_engine, practitioner_id, full_name=None, position=None, email=None, phone_number=None, active=None):
    """
    Update a practitioner's information in the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): SQLAlchemy database engine.
        practitioner_id (int): Practitioner ID.
        full_name (str, optional): Updated full name of the practitioner. Defaults to None.
        position (str, optional): Updated position of the practitioner. Defaults to None.
        email (str, optional): Updated email address of the practitioner. Defaults to None.
        phone_number (str, optional): Updated phone number of the practitioner. Defaults to None.
        active (bool, optional): Updated flag indicating if the practitioner is active. Defaults to None.

    Returns:
        None
    """
    # Create a session using the provided database engine
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        # Get the Practitioner to update based on the ID
        practitioner = session.query(Practitioner).filter_by(id=practitioner_id).first()
        if practitioner is None:
            print(f"Error: Practitioner with ID {practitioner_id} not found")
            return
        if full_name is not None:
            practitioner.full_name = full_name
        if position is not None:
            practitioner.position = position
        if email is not None:
            practitioner.email = email
        if phone_number is not None:
            practitioner.phone_number = phone_number
        if active is not None:
            practitioner.active = active
        try:
            # Commit the changes to the database
            session.commit()
            print(f"Practitioner with ID {practitioner_id} updated successfully")
        except Exception as e:
            session.rollback()
            print("Error: Failed to update Practitioner")

def delete_practitioner(db_engine, practitioner_id):
    """
    Mark a practitioner as inactive in the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): SQLAlchemy database engine.
        practitioner_id (int): Practitioner ID.

    Returns:
        None
    """
    # Create a session using the provided database engine
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        # Get the Practitioner to delete based on the ID
        practitioner = session.query(Practitioner).filter_by(id=practitioner_id).first()
        if practitioner is None:
            print(f"Error: Practitioner with ID {practitioner_id} not found")
            return
        try:
            # Mark the Practitioner as inactive (set the 'active' field to False) and commit the changes
            practitioner.active = False
            session.commit()
            print(f"Practitioner with ID {practitioner_id} marked as inactive successfully")
        except Exception as e:
            session.rollback()
            print("Error: Failed to mark Practitioner as inactive")

def verify_practitioner(db_engine, email):
    """
    Verify the access rights of a practitioner based on the email.

    Args:
        db_engine (sqlalchemy.engine.Engine): SQLAlchemy database engine.
        email (str): Email address of the practitioner.

    Returns:
        tuple: Tuple containing the access status, practitioner ID, and role.
    """
    # Create a session using the provided database engine
    Session = sessionmaker(bind=db_engine)
    with Session() as session:
        try:
            # Retrieve the practitioner based on the email
            practitioner = session.query(Practitioner).filter_by(email=email).first()
            if practitioner is not None:
                if practitioner.position == "Administrador":
                    # Return access authorized with the practitioner's ID and role
                    return "Access authorized", practitioner.id, "Administrator"
                else:
                    return "Access authorized", practitioner.id, "Practitioner"
            else:
                return "Access denied", "no_id", "no_role"
        except Exception as e:
            print("Error retrieving practitioner data:", str(e))
            return "Access denied", "no_id", "no_role"
