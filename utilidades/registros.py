from utilidades.conexion import connect
from psycopg2 import errors

def registrar(cedula, nombres, apellidos, fecha_nacimiento, ocupacion, estado_civil, facultad, nombre_preferido, lugar_nacimiento, lugar_residencia, contacto_emergencia, telefono_emergencia, antecendentes_familiares, antecendentes_personales, antecendentes_clinicos):

    try:
        conn = connect()
        cur = conn.cursor()
        nombre = nombres + " " + apellidos
        query = "INSERT INTO paciente(cedula,nombre,fecha_nacimiento,ocupacion,estado_civil, facultad, nombre_preferido, lugar_nacimiento, lugar_residencia, contacto_emergencia, telefono_emergencia, antecedentes_familiares, antecedentes_personales, antecedentes_clinicos) values('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}','{12}','{13}')".format(cedula, nombre, fecha_nacimiento, ocupacion, estado_civil, facultad, nombre_preferido, lugar_nacimiento, lugar_residencia, contacto_emergencia, telefono_emergencia, antecendentes_familiares, antecendentes_personales, antecendentes_clinicos)
        cur.execute(query)
        conn.commit()
        return "Paciente registrado"
    except (Exception, errors.UniqueViolation) as error:
        return("El paciente ya se encuentra registrado")
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')