import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

from data.actions.encounter_actions import add_encounter
from data.create_database import Base, Encounter, Patient, Practitioner


class TestAddEncounter(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database
        self.db_engine = create_engine("sqlite:///../bienestar.db")
        # Base.metadata.create_all(self.db_engine)

    def test_add_encounter(self):
        # Create a Session
        Session = sessionmaker(bind=self.db_engine)
        session = Session()

        # Add a patient and a practitioner to the database
        # Create a new Patient instance
        patient = Patient(
            id="2",
            first_name="John",
            first_family_name="Doe",
            birth_date=datetime.datetime(1997, 3, 2),
            phone_number="555-555-5555",
            email="john.doe@example.com",
        )

        # Create a new Practitioner instance
        practitioner = Practitioner(
            id="2",
            full_name="Jane Doe",
            phone_number="555-555-5555",
            email="jane.doe@example.com",
            position="Pediatrics",
        )

        session.add(patient)
        session.add(practitioner)
        session.commit()

        # Define test data
        encounter_type = "Follow-up"
        topics_boarded = "Patient reports symptoms of headache and fatigue"
        date = datetime.datetime(2022, 3, 2)
        activities_sent = "Prescribed medication"
        attachments = "N/A"
        patient_id = "2"
        practitioner_id = "2"

        # Call the add_encounter function
        add_encounter(
            db_engine=self.db_engine,
            encounter_type=encounter_type,
            topics_boarded=topics_boarded,
            date=date,
            activities_sent=activities_sent,
            attachments=attachments,
            patient_id=patient_id,
            practitioner_id=practitioner_id,
        )

        # Check that the Encounter was added to the database
        result = session.query(Encounter).filter_by(patient_id=patient_id).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.encounter_type, encounter_type)
        self.assertEqual(result.topics_boarded, topics_boarded)
        self.assertEqual(result.activities_sent, activities_sent)
        self.assertEqual(result.attachments, attachments)
        self.assertEqual(result.patient_id, patient_id)
        self.assertEqual(result.practitioner_id, practitioner_id)

        # Close the session
        session.close()


if __name__ == "__main__":
    unittest.main()
