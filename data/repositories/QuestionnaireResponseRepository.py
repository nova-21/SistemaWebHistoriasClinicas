import pandas as pd
import pytz
from sqlalchemy import cast
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
import datetime
from data.database_declaration import QuestionnaireResponse, Questionnaire

def add_questionnaire_response(db_engine, date, patient_id, questionnaire_id):
    """
    Adds a questionnaire response to the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): The SQLAlchemy database engine.
        date (str or datetime.datetime): The date of the questionnaire response.
        patient_id (int): The ID of the patient.
        questionnaire_id (int): The ID of the questionnaire.

    Returns:
        str: A message indicating the success or failure of adding the questionnaire response.
    """
    res = get_pending_questionnaire(db_engine, date, patient_id, questionnaire_id)
    print(res)
    if len(res) == 0:
        add_questionnaire(
            db_engine, date, patient_id, "pending", questionnaire_id, "", ""
        )

def add_questionnaire(
    db_engine, date, patient_id, state, questionnaire_id, result, answers
):
    """
    Adds a questionnaire to the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): The SQLAlchemy database engine.
        date (str or datetime.datetime): The date of the questionnaire.
        patient_id (int): The ID of the patient.
        state (str): The state of the questionnaire.
        questionnaire_id (int): The ID of the questionnaire.
        result (str): The result of the questionnaire.
        answers (str): The answers of the questionnaire.

    Returns:
        str: A message indicating the success or failure of adding the questionnaire.
    """
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    elif isinstance(date, datetime):
        date = date.date()

    # Create a new QuestionnaireResponse instance
    questionnaire_response = QuestionnaireResponse()
    questionnaire_response.date = date
    questionnaire_response.patient_id = patient_id
    questionnaire_response.state = state
    questionnaire_response.questionnaire_id = questionnaire_id
    questionnaire_response.result = result
    questionnaire_response.answers = answers

    try:
        # Add the new QuestionnaireResponse to the session and commit
        session.add(questionnaire_response)
        session.commit()
        return "Questionnaire response added successfully."
    except IntegrityError:
        # Rollback the session in case of IntegrityError (e.g. duplicate primary key)
        session.rollback()
        message = (
            "Error adding questionnaire response, please check your data and try again."
        )
        print(message)
        return message
    finally:
        # Close the session
        session.close()

def get_pending_questionnaire_responses(db_engine, date, patient_id):
    """
    Retrieves pending questionnaire responses from the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): The SQLAlchemy database engine.
        date (str or datetime.datetime): The date of the questionnaire responses.
        patient_id (int): The ID of the patient.

    Returns:
        pandas.DataFrame: A DataFrame containing the pending questionnaire responses.
    """
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Query the database for QuestionnaireResponse instances with matching date, patient_id, and state='pending'
    pending_responses = (
        session.query(QuestionnaireResponse, Questionnaire.name)
            .join(Questionnaire, QuestionnaireResponse.questionnaire_id == Questionnaire.id)
            .filter(QuestionnaireResponse.date == date, QuestionnaireResponse.patient_id == patient_id,
                    QuestionnaireResponse.state == "pending")
            .all()
    )

    # Close the session
    session.close()
    df = pd.DataFrame(
        [
            {"Cuestionario": response.name, "state": "Pendiente" if response[0].state == "pending" else response[0].state}
            for response in pending_responses
        ]
    )

    # Return the list of matching QuestionnaireResponse instances
    return df

def get_questionnaire_results(db_engine, date, patient_id):
    """
    Retrieves questionnaire results from the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): The SQLAlchemy database engine.
        date (str or datetime.datetime): The date of the questionnaire results.
        patient_id (int): The ID of the patient.

    Returns:
        pandas.DataFrame: A DataFrame containing the questionnaire results.
    """
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Query the database for QuestionnaireResponse instances with matching date, patient_id, and state='pending'
    responses_answers = (
        session.query(
            Questionnaire.title,
            QuestionnaireResponse.points,
            QuestionnaireResponse.result,
        )
        .join(Questionnaire, Questionnaire.id == QuestionnaireResponse.questionnaire_id)
        .filter(
            QuestionnaireResponse.date == date,
            QuestionnaireResponse.patient_id == patient_id,
            QuestionnaireResponse.state == "finished",
        )
        .all()
    )

    # Close the session
    session.close()
    df = pd.DataFrame(
        [
            {
                "Nombre Cuestionario": answer.title,
                "Puntaje": answer.points,
                "Resultado": answer.result,
            }
            for answer in responses_answers
        ]
    )

    # Return the list of matching QuestionnaireResponse instances
    return df

def get_questionnaire_answers(db_engine, date, patient_id):
    """
    Retrieves questionnaire answers from the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): The SQLAlchemy database engine.
        date (str or datetime.datetime): The date of the questionnaire answers.
        patient_id (int): The ID of the patient.

    Returns:
        pandas.DataFrame: A DataFrame containing the questionnaire answers.
    """
    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    # Query the database for QuestionnaireResponse instances with matching date, patient_id, and state='pending'
    responses_answers = (
        session.query(QuestionnaireResponse.id, QuestionnaireResponse.answers)
        .filter(
            QuestionnaireResponse.date == date,
            QuestionnaireResponse.patient_id == patient_id,
            QuestionnaireResponse.state == "finished",
        )
        .all()
    )

    # Close the session
    session.close()
    df = pd.DataFrame(
        [
            {"Cuestionario": answer.id, "Resultado": answer.answers}
            for answer in responses_answers
        ]
    )

    # Return the list of matching QuestionnaireResponse instances
    return df

def get_pending_questionnaire(db_engine, date, patient_id, questionnaire_id):
    """
    Retrieves pending questionnaires from the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): The SQLAlchemy database engine.
        date (str or datetime.datetime): The date of the questionnaires.
        patient_id (int): The ID of the patient.
        questionnaire_id (int): The ID of the questionnaire.

    Returns:
        list: A list of matching QuestionnaireResponse instances.
    """
    from datetime import datetime, timedelta
    import pytz

    # Create a Session
    Session = sessionmaker(bind=db_engine)
    session = Session()

    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d").date()
    elif isinstance(date, datetime):
        date = date.date()

    # Query the database for QuestionnaireResponse instances with matching date, patient_id, and state='pending'
    pending_responses = (
        session.query(QuestionnaireResponse.id)
        .filter_by(
            patient_id=patient_id,
            questionnaire_id=questionnaire_id,
            state="pending",
            date=date,
        )
        .all()
    )

    # Close the session
    session.close()

    # Return the list of matching QuestionnaireResponse instances
    return pending_responses
