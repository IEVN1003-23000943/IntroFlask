from flask import Blueprint, jsonify, request
from database import mysql

alumnos_bp = Blueprint(
    'alumnos',
    __name__,
    url_prefix='/api/alumnos'
)

def fila_a_diccionario(cursor, fila):
  columnas = [columna[0] for columna in cursor.description]
  return dict(zip(columnas, fila))

@alumnos_bp.route("/", methods=["GET"])
def lista_alumnos():
  cursor = None
  try:
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM alumnos")
    datos = cursor.fetchall()
    alumnos = []
    for filas in datos:
      alumno = {
          "matricula": filas[0],
          "nombre": filas[1],
          "apaterno": filas[2],
          "amaterno": filas[3],
          "correo": filas[4],
      }
      alumnos.append(alumno)

    return jsonify(
        {"alumnos": alumnos, "mensaje": "Lista de Alumnos", "exito": True}
    )
  except Exception as ex:
    return jsonify({"mensaje": f"Error: {ex}", "exito": False}), 500
  finally:
    if cursor is not None:
      cursor.close()

@alumnos_bp.route("/<string:matricula>", methods=["GET"])
def leer_alumno(matricula):
  cursor = None
  try:
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT * FROM alumnos WHERE matricula = %s", (matricula,)
    )
    fila = cursor.fetchone()
    if fila is None:
      return (
          jsonify({"mensaje": "Alumno no encontrado", "exito": False}),
          404,
      )
    alumno = fila_a_diccionario(cursor, fila)
    return jsonify({"alumno": alumno, "exito": True}), 200
  except Exception:
    return (
        jsonify(
            {"mensaje": "Error al consultar el alumno", "exito": False}
        ),
        500,
    )
  finally:
    if cursor is not None:
      cursor.close()

@alumnos_bp.route("/", methods=["POST"])
def registrar_alumno():
  datos = request.get_json(silent=True)
  if not isinstance(datos, dict):
    return (
        jsonify({"mensaje": "Se requiere un objeto JSON", "exito": False}),
        400,
    )

  campos = ["matricula", "nombre", "apaterno", "amaterno", "correo"]

  if any(
      campo not in datos
      or not isinstance(datos[campo], str)
      or not datos[campo].strip()
      for campo in campos
  ):
    return (
        jsonify({"mensaje": "Faltan campos obligatorios", "exito": False}),
        400,
    )

  cursor = None
  try:
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT matricula FROM alumnos WHERE matricula = %s",
        (datos["matricula"].strip(),),
    )

    if cursor.fetchone() is not None:
      return (
          jsonify({"mensaje": "La matricula ya existe", "exito": False}),
          409,
      )

    sql = """INSERT INTO alumnos (matricula, nombre, apaterno, amaterno, correo) 
             VALUES (%s, %s, %s, %s, %s)"""
    valores = tuple(datos[campo].strip() for campo in campos)

    cursor.execute(sql, valores)
    mysql.connection.commit()

    return (
        jsonify({"mensaje": "Alumno registrado con exito", "exito": True}),
        201,
    )

  except Exception:
    mysql.connection.rollback()
    return (
        jsonify({"mensaje": "Error al registrar alumno", "exito": False}),
        500,
    )

  finally:
    if cursor is not None:
      cursor.close()

@alumnos_bp.route("/<string:matricula>", methods=["PUT"])
def modificar_alumno(matricula):
  datos = request.get_json(silent=True)
  if not datos:
    return (
        jsonify({"mensaje": "No se recibieron datos para modificar"}),
        400,
    )

  nombre = datos.get("nombre")
  apaterno = datos.get("apaterno")
  amaterno = datos.get("amaterno")
  correo = datos.get("correo")

  if not nombre or not apaterno or not correo:
    return (
        jsonify({
            "mensaje": "Nombre, apellido paterno y correo son obligatorios"
        }),
        400,
    )

  cursor = None
  try:
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT matricula FROM alumnos WHERE matricula = %s", (matricula,)
    )
    alumno = cursor.fetchone()

    if not alumno:
      return (
          jsonify({"mensaje": "No existe el alumno con esa matricula"}),
          404,
      )

    sql = """UPDATE alumnos 
             SET nombre = %s, apaterno = %s, amaterno = %s, correo = %s 
             WHERE matricula = %s"""

    cursor.execute(sql, (nombre, apaterno, amaterno, correo, matricula))
    mysql.connection.commit()

    return (
        jsonify({
            "mensaje": "Alumno modificado correctamente",
            "matricula": matricula,
            "exito": True,
        }),
        200,
    )

  except Exception as e:
    mysql.connection.rollback()
    return (
        jsonify({"mensaje": "Error al actualizar alumno", "exito": str(e)}),
        500,
    )

  finally:
    if cursor is not None:
      cursor.close()

@alumnos_bp.route("/<string:matricula>",methods=["DELETE"])
def eliminar_alumno(matricula):
  cursor = None
  try:
    cursor=mysql.connection.cursor()
    cursor.execute(
      "SELECT matricula FROM alumnos WHERE matricula = %s",(matricula,)
    )
    alumno = cursor.fetchone()
    if not alumno:
      return jsonify({
        "mensaje":"No existe un alumno con esa matricula"
      }),404
    cursor.execute(
      "DELETE FROM alumnos WHERE matricula = %s",(matricula,)
    )
    mysql.connection.commit()
    return jsonify({
      "mensaje":"Alumno elimina con exito",
      "matricula":matricula
    }),200
  except Exception as e:
      mysql.connection.rollback()
      return (
          jsonify({"mensaje": "Error al eliminar alumno", "exito": str(e)}),
          500,
      )
  
  finally:
      if cursor is not None:
        cursor.close()
