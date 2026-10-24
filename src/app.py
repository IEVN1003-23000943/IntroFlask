from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL

from config import config

app = Flask(__name__)
CORS(app)
con = MySQL(app)


def fila_a_diccionario(cursor, fila):
  columnas = [columna[0] for columna in cursor.description]
  return dict(zip(columnas, fila))


@app.route("/alumnos", methods=["GET"])
def lista_alumnos():
  cursor = None
  try:
    cursor = con.connection.cursor()
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


@app.route("/alumnos/<string:matricula>", methods=["GET"])
def leer_alumno(matricula):
  cursor = None
  try:
    cursor = con.connection.cursor()
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


@app.route("/alumnos", methods=["POST"])
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
    cursor = con.connection.cursor()
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
    con.connection.commit()

    return (
        jsonify({"mensaje": "Alumno registrado con exito", "exito": True}),
        201,
    )

  except Exception:
    con.connection.rollback()
    return (
        jsonify({"mensaje": "Error al registrar alumno", "exito": False}),
        500,
    )

  finally:
    if cursor is not None:
      cursor.close()


def pagina_no_encontrada(error):
  return "<h1>Página no encontrada</h1>", 404


if __name__ == "__main__":
  app.config.from_object(config["development"])
  app.register_error_handler(404, pagina_no_encontrada)
  app.run(host="0.0.0.0", port=5000)