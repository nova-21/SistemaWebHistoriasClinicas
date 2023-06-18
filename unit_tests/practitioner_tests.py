import random
import unittest
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from data.database_connection import create_engine_conection
from data.database_declaration import Base, Patient
from data.repositories import PatientRepository

# Set up the test database engine
engine = create_engine_conection()
Base.metadata.create_all(engine)

# Instantiate a Faker object for generating random data
fake = Faker("es_MX")


class TestAddPatient(unittest.TestCase):
    """
    A test case class for adding patients to the database.
    """

    def test_add_patient(self):
        """
        Test for adding a patient to the database.
        """
        # Add 2000 patients
        for i in range(2000):
            # Generate random patient data
            id = fake.random_int(1000000000, 9999999999)
            first_name = fake.first_name()
            second_name = fake.first_name()
            first_family_name = fake.last_name()
            second_family_name = fake.last_name()
            preferred_name = fake.first_name()
            birth_date = fake.date_of_birth()
            sex = random.choice(["Masculino", "Femenino"])
            gender = random.choice(["Hombre", "Mujer", "Otro"])
            sexual_orientation = random.choice(
                ["Heterosexual", "Homosexual", "Bisexual", "Pansexual", "Asexual"]
            )
            phone_number = f"{random.randint(1000000000, 9999999999)}"
            email = fake.email()
            profession_occupation = fake.job()[:20]
            marital_status = random.choice(
                ["Soltero", "Casado", "Divorciado", "Viudo", "Union libre"]
            )
            patient_type = random.choice(
                ["Estudiante", "Docente", "Administrativo", "Egresado"]
            )
            faculty_dependence = random.choice(["Facultad 1", "Facultad 2", "Facultad 3"])
            career = fake.job()[:20]
            semester = str(fake.random_int(1, 12))
            city_born = fake.city()[:20]
            city_residence = fake.city()[:20]
            address = fake.address()[:50]
            children = fake.random_int(0, 5)
            lives_with = random.choice(["Solo", "Con pareja", "Con familia", "Con amigos"])
            emergency_contact_name = fake.name()[:20]
            emergency_contact_relation = random.choice(
                ["Padre", "Madre", "Hermano", "Hermana", "Amigo"]
            )
            emergency_contact_phone = f"{random.randint(1000000000, 9999999999)}"
            family_history = "Test 123"
            personal_history = "Test 123"
            habits = "Smoking"
            extra_information = "Test 123"
            active = random.choice([True, False])

            # Add the patient to the database
            result = PatientRepository.add_patient(
                engine,
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
                habits,
                extra_information,
                active,
            )

            # Ensure that the patient was added successfully
            self.assertEqual(result, "Paciente registrado")


if __name__ == "__main__":
    unittest.main()
