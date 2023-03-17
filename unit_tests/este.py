from sqlalchemy import create_engine, Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship


from data.create_database import Appointment

engine = create_engine(
    "sqlite:///C:/Users/David/Documents/GitHub/SistemaWebHistoriasClinicas/base_de_datos/bienestar.db"
)
Session = sessionmaker(bind=engine)
session = Session()

appointment = Appointment()
appointment.appointment_type = "booked"
appointment.status = "status"
appointment.reason = "reason"
appointment.patient_id = "5"
appointment.practitioner_id = "3"
session.add(appointment)
session.commit()
