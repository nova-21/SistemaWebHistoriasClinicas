import unittest
from sqlalchemy.orm import sessionmaker
import random
import datetime
from data.database_connection import create_engine_conection
from data.database_declaration import Appointment, Encounter, Patient, Practitioner
from utilities.lists import list_encounter_types

class TestInsertAppointments(unittest.TestCase):
    """
    A test case class for inserting appointments into the database.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up the test database engine and session.
        """
        cls.engine = create_engine_conection()
        Session = sessionmaker(cls.engine)
        cls.db_session = Session()

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the test database engine and session.
        """
        cls.db_session.close()
        cls.engine.dispose()

    def test_insert_appointments(self):
        """
        Test for inserting appointments into the database.
        """
        patient_ids = self.db_session.query(Patient.id).all()
        practitioner_ids = self.db_session.query(Practitioner.id).all()

        for i in range(500):
            # Generate a random date between 1 and 365 days ago
            days_ago = random.randint(1, 365)
            random_date = datetime.datetime.today() - datetime.timedelta(days=days_ago)
            appointment_date = datetime.datetime(
                random_date.year, random_date.month, random_date.day
            )
            e_t = random.choice(list_encounter_types)
            appointment = Appointment(
                status="atendida",
                date=appointment_date,
                patient_id=random.choice(patient_ids)[0],
                appointment_type=random.choice(["Primera vez", "Subsecuente"]),
                encounter_type=e_t,
                practitioner_id=random.choice(practitioner_ids)[0],
            )
            encounter = Encounter(
                date=appointment_date,
                patient_id=appointment.patient_id,
                encounter_type=e_t,
                practitioner_id=appointment.practitioner_id,
            )
            self.db_session.add(appointment)
            self.db_session.add(encounter)

        self.db_session.commit()

    def test_insert_appointments_subsecuentes(self):
        """
        Test for inserting subsequent appointments into the database.
        """
        patient_ids = self.db_session.query(Patient.id).all()
        practitioner_ids = self.db_session.query(Practitioner.id).all()

        for i in range(100):
            # Generate a random date between 1 and 365 days ago
            days_ago = random.randint(1, 365)
            random_date = datetime.datetime.today() - datetime.timedelta(days=days_ago)
            appointment_date = datetime.datetime(
                random_date.year, random_date.month, random_date.day
            )
            e_t = random.choice(list_encounter_types)
            appointment = Appointment(
                status="no_atendida",
                date=appointment_date,
                patient_id=random.choice(patient_ids)[0],
                appointment_type=random.choice(["Primera vez", "Subsecuente"]),
                encounter_type=e_t,
                practitioner_id=random.choice(practitioner_ids)[0],
                reason=random.choice([
                    "Ausentismo",
                    "Reagendamiento por el paciente",
                    "Reagendamiento por el tratante",
                ])
            )
            self.db_session.add(appointment)

        self.db_session.commit()

if __name__ == "__main__":
    unittest.main()
