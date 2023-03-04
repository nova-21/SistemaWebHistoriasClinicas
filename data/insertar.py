from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from create_database import Practitioner, Encounter, Patient, Appointment

engine = create_engine("sqlite:///bienestar.db")

Session = sessionmaker(bind=engine)
session = Session()

# tratante1 = Practitioner(
#     id="1234567890",
#     full_name="Juan Carlos Davalos Cuenca",
#     position="Psicologo clinico",
#     email="juan.davalos@ucuenca.edu.ec",
#     phone_number="0994834336",
# )

# paciente1 = Patient(
#     id="0106785215",
#     first_name="Alex",
#     second_name="David",
#     first_family_name="Pinos",
#     second_family_name="Palacios",
#     preferred_name="",
#     birth_date=date.today(),
#     sex="",
#     gender="",
#     sexual_orientation="",
#     phone_number="",
#     email="",
#     profession_occupation="",
#     marital_status="",
#     patient_type="",
#     faculty_dependence="",
#     career="",
#     semester="",
#     city_born="",
#     city_residence="",
#     address="",
#     children="",
#     lives_with="",
#     emergency_contact_name="",
#     emergency_contact_relation="",
#     emergency_contact_phone="",
#     family_history="",
#     personal_history="",
#     extra_information=""
# )

# cita1 = Appointment(
#     appointment_type="Subsecuente",
#     status="",
#     reason="",
#     date=date.today(),
#     time="10:00",
#     patient_id="0106785215",
#     practitioner_id="1234567890"
# )

# sesion1 = Encounter(
#     patient_id="0106785215",
#     date=date.today(),
#     encounter_type="Psicoterapia",
#     topics_boarded="Test",
#     practitioner_id="1234567890",
#     activities_sent="ninguna",
#     attachments="Nada",
# )

# session.add(tratante1)
# session.add(paciente1)
# session.add(cita1)
# session.add(sesion1)

session.commit()
