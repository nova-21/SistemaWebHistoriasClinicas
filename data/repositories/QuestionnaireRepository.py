from sqlalchemy.orm import sessionmaker
from data.database_declaration import Questionnaire

def get_questionnaires(db_engine):
    """
    Retrieve a list of questionnaires from the database.

    Args:
        db_engine (sqlalchemy.engine.Engine): SQLAlchemy database engine.

    Returns:
        list: List of tuples containing questionnaire ID and name.
    """
    # Create a session using the provided database engine
    Session = sessionmaker(bind=db_engine)
    with Session() as session:

        try:
            # Query the database for Questionnaire instances and retrieve the ID and name
            questionnaires = session.query(Questionnaire.id, Questionnaire.name).all()
            # Return the list of questionnaires
            return questionnaires
        except Exception as e:
            print("Error retrieving questionnaires:", str(e))
            return []
