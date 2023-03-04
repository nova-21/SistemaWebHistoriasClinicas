from bin.conexion import connect
from psycopg2 import errors

def insert_patient(id, first_name, second_name, first_family_name, second_family_name,
                                      preferred_name, birth_date,
                                      sex,
                                      gender,
                                      sexual_orientation,
                                      phone_number,
                                      email,
                                      profession_ocupation,
                                      maritalStatus,
                                      patient_type,
                                      faculty_dependance,
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
                                      extra_information):

    try:
        conn = connect()
        cur = conn.cursor()
        query = "INSERT INTO paciente values('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}')".format(id, first_name, second_name, first_family_name, second_family_name,
                                      preferred_name, birth_date,
                                      sex,
                                      gender,
                                      sexual_orientation,
                                      phone_number,
                                      email,
                                      profession_ocupation,
                                      maritalStatus,
                                      patient_type,
                                      faculty_dependance,
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
                                      extra_information)
        cur.execute(query)
        conn.commit()
        return "Paciente registrado"
    except (Exception, errors.UniqueViolation) as error:
        return("El paciente ya se encuentra registrado")
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


def book_appointment(patient_id, practitioner_id, appointment_type, date, time):
    try:
        conn = connect()
        cur = conn.cursor()
        query = "INSERT INTO cita(cedula_paciente,tratante_id,fecha,hora,primera_cita) values('{0}','{1}','{2}','{3}','{4}')".format(patient_id, practitioner_id, date, time,appointment_type)
        cur.execute(query)
        conn.commit()
        return "Cita registrada"
    except (Exception, errors.UniqueViolation) as error:
        return("Cita ya registrada")
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')