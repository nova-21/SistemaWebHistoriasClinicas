import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from data.create_database import QuestionnaireResponse, Questionnaire


def get_questionnaires(db_engine):
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Query the database for QuestionnaireResponse instances with matching date, patient_id, and state='pending'
    questionnaires = session.query(Questionnaire.id, Questionnaire.name).all()

    # Close the session
    session.close()

    # Return the list of matching QuestionnaireResponse instances
    return questionnaires
