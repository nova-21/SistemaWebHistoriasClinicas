from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from data.create_database import Practitioner


def add_practitioner(db_engine, id, full_name, position, email, phone_number, active):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Create a new Practitioner instance
    practitioner = Practitioner(
        id=id,
        full_name=full_name,
        position=position,
        email=email,
        phone_number=phone_number,
        active=active,
    )

    try:
        # Add the new Practitioner to the session and commit
        session.add(practitioner)
        session.commit()
        print("New Practitioner added successfully")
    except IntegrityError:
        # Rollback the session in case of IntegrityError (e.g. duplicate primary key)
        session.rollback()
        print("Error: Practitioner with the same ID already exists")
    finally:
        # Close the session
        session.close()


def update_practitioner(
    db_engine,
    id,
    full_name=None,
    position=None,
    email=None,
    phone_number=None,
    active=None,
):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Get the Practitioner to update
    practitioner = session.query(Practitioner).filter_by(id=id).first()

    if practitioner is None:
        print(f"Error: Practitioner with ID {id} not found")
        return

    # Update the Practitioner attributes if they're not None
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
        print(f"Practitioner with ID {id} updated successfully")
    except:
        # Rollback the session in case of an error
        session.rollback()
        print("Error: Failed to update Practitioner")
    finally:
        # Close the session
        session.close()


def delete_practitioner(db_engine, id):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Get the Practitioner to update
    practitioner = session.query(Practitioner).filter_by(id=id).first()

    if practitioner is None:
        print(f"Error: Practitioner with ID {id} not found")
        return

    try:
        # Set the active field to False for the Practitioner
        practitioner.active = False
        session.commit()
        print(f"Practitioner with ID {id} marked as inactive successfully")
    except:
        # Rollback the session in case of an error
        session.rollback()
        print("Error: Failed to mark Practitioner as inactive")
    finally:
        # Close the session
        session.close()
