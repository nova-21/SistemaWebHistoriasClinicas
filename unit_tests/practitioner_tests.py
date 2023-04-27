import os

from data.actions.practitioner_actions import add_practitioner
from data.create_database import Base, Practitioner
import unittest
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set up the test database engine
engine = create_engine("sqlite:///../data/bienestar.db")
Base.metadata.create_all(engine)


class TestAddPractitioner(unittest.TestCase):
    def setUp(self):
        # Create a SQLite database in memory for testing
        self.engine = create_engine(os.environ.get("DATABASE"))
        Base.metadata.create_all(self.engine)

        # Create a Session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def tearDown(self):
        # Close the session and dispose of the engine
        self.session.close()
        self.engine.dispose()

    def test_add_practitioner(self):
        # Create 20 random practitioners using the faker library
        fake = Faker("es_MX")
        practitioners = []
        for i in range(20):
            practitioner = Practitioner(
                id=fake.unique.random_number(digits=6),
                full_name=fake.name()[:20],
                position=fake.job()[:20],
                email=fake.email(),
                phone_number=fake.phone_number()[:10],
                active=fake.boolean(),
            )
            practitioners.append(practitioner)

        # Add the practitioners to the database using the add_practitioner() method
        for practitioner in practitioners:
            add_practitioner(
                self.engine,
                practitioner.id,
                practitioner.full_name,
                practitioner.position,
                practitioner.email,
                practitioner.phone_number,
                practitioner.active,
            )

        # Check that the practitioners were added to the database
        practitioner_count = self.session.query(Practitioner).count()



if __name__ == "__main__":
    unittest.main()
