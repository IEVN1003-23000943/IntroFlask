from flask import Blueprint, jsonify, request
from database import mysql

maestros_bp = Blueprint(
    'maestros',
    __name__,
    url_prefix='/api/maestros'
)

def fila_a_diccionario(cursor, fila):
  columnas = [columna[0] for columna in cursor.description]
  return dict(zip(columnas, fila))

@maestros_bp.route("/", methods=["GET"])
def lista_maestros():
  cursor = None
  try:
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM maestros")
    datos = cursor.fetchall()
    maestros = []
    for filas in datos:
      maestro = {
          "idmaestro": filas[0],
          "nombre": filas[1],
          "apaterno": filas[2],
          "amaterno": filas[3],
          "correo": filas[4],
      }
      maestros.append(maestro)

    return jsonify(
        {"Maestros": maestros, "mensaje": "Lista de Maestros", "exito": True}
    )
  except Exception as ex:
    return jsonify({"mensaje": f"Error: {ex}", "exito": False}), 500
  finally:
    if cursor is not None:
      cursor.close()
    
    
    
@maestros_bp.route('/<string:idmaestro>', methods=['GET'])
def leer_maestro(idmaestro):
  cursor = None
  try:
    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT * FROM maestros WHERE idmaestro = %s', (idmaestro,)
    )
    fila = cursor.fetchone()
    if fila is None:
      return (
          jsonify({'mensaje': 'Maestro no encontrado', 'exito': False}),
          404,
      )
    maestro = fila_a_diccionario(cursor, fila)
    return jsonify({'maestro': maestro, 'exito': True}), 200
  except Exception:
    return (
        jsonify(
            {'mensaje': 'Error al consultar el maestro', 'exito': False}
        ),
        500,
    )
  finally:
    if cursor is not None:
      cursor.close()


@maestros_bp.route('/', methods=['POST'])
def registrar_maestro():
  datos = request.get_json(silent=True)
  if not isinstance(datos, dict):
    return (
        jsonify({'mensaje': 'Se requiere un objeto JSON', 'exito': False}),
        400,
    )

  campos = ['idmaestro', 'nombre', 'apaterno', 'amaterno', 'correo']

  if any(
      campo not in datos
      or not isinstance(datos[campo], str)
      or not datos[campo].strip()
      for campo in campos
  ):
    return (
        jsonify({'mensaje': 'Faltan campos obligatorios', 'exito': False}),
        400,
    )

  cursor = None
  try:
    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT idmaestro FROM maestros WHERE idmaestro = %s',
        (datos['idmaestro'].strip(),),
    )

    if cursor.fetchone() is not None:
      return (
          jsonify({'mensaje': 'El idmaestro ya existe', 'exito': False}),
          409,
      )

    sql = """INSERT INTO maestros (idmaestro, nombre, apaterno, amaterno, correo) 
             VALUES (%s, %s, %s, %s, %s)"""
    valores = tuple(datos[campo].strip() for campo in campos)

    cursor.execute(sql, valores)
    mysql.connection.commit()

    return (
        jsonify({'mensaje': 'Maestro registrado con éxito', 'exito': True}),
        201,
    )

  except Exception as ex:
    mysql.connection.rollback()
    return (
        jsonify(
            {'mensaje': f'Error al registrar maestro: {ex}', 'exito': False}
        ),
        500,
    )

  finally:
    if cursor is not None:
      cursor.close()


@maestros_bp.route('/<string:idmaestro>', methods=['PUT'])
def modificar_maestro(idmaestro):
  datos = request.get_json(silent=True)
  if not datos:
    return (
        jsonify({
            'mensaje': 'No se recibieron datos para modificar',
            'exito': False,
        }),
        400,
    )

  nombre = datos.get('nombre')
  apaterno = datos.get('apaterno')
  amaterno = datos.get('amaterno')
  correo = datos.get('correo')

  if not nombre or not apaterno or not correo:
    return (
        jsonify({
            'mensaje': 'Nombre, apellido paterno y correo son obligatorios',
            'exito': False,
        }),
        400,
    )

  cursor = None
  try:
    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT idmaestro FROM maestros WHERE idmaestro = %s', (idmaestro,)
    )
    maestro = cursor.fetchone()

    if not maestro:
      return (
          jsonify({
              'mensaje': 'No existe el maestro con ese id',
              'exito': False,
          }),
          404,
      )

    sql = """UPDATE maestros 
             SET nombre = %s, apaterno = %s, amaterno = %s, correo = %s 
             WHERE idmaestro = %s"""

    cursor.execute(sql, (nombre, apaterno, amaterno, correo, idmaestro))
    mysql.connection.commit()

    return (
        jsonify({
            'mensaje': 'Maestro modificado correctamente',
            'idmaestro': idmaestro,
            'exito': True,
        }),
        200,
    )

  except Exception as e:
    mysql.connection.rollback()
    return (
        jsonify({'mensaje': 'Error al actualizar maestro', 'exito': str(e)}),
        500,
    )

  finally:
    if cursor is not None:
      cursor.close()


@maestros_bp.route('/<string:idmaestro>', methods=['DELETE'])
def eliminar_maestro(idmaestro):
  cursor = None
  try:
    cursor = mysql.connection.cursor()
    cursor.execute(
        'SELECT idmaestro FROM maestros WHERE idmaestro = %s', (idmaestro,)
    )
    maestro = cursor.fetchone()
    if not maestro:
      return (
          jsonify({
              'mensaje': 'No existe un maestro con ese id',
              'exito': False,
          }),
          404,
      )

    cursor.execute('DELETE FROM maestros WHERE idmaestro = %s', (idmaestro,))
    mysql.connection.commit()

    return (
        jsonify({
            'mensaje': 'Maestro eliminado con éxito',
            'idmaestro': idmaestro,
            'exito': True,
        }),
        200,
    )
  except Exception as e:
    mysql.connection.rollback()
    return (
        jsonify({'mensaje': 'Error al eliminar maestro', 'exito': str(e)}),
        500,
    )
  finally:
    if cursor is not None:
      cursor.close()