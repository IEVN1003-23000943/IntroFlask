from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS

from config import config

app = Flask(__name__)
CORS(app)
con = MySQL(app)

@app.route("/alumnos", methods=["GET"])
def lista_alumnos():
    try:
        cursor = con.connection.cursor()
        sql = "select * from alumnos"
        cursor.execute(sql)
        datos = cursor.fetchall()
        alumnos = []
        for filas in datos:
            alumno = {
                "matricula": filas[0],
                "nombre": filas[1],
                "apaterno": filas[2],
                "amaterno": filas[3],
                "correo": filas[4]
            }
            alumnos.append(alumno)
        
        return jsonify({'alumnos': alumnos, 'mensaje': "Lista de Alumnos", 'exito': True})
    except Exception as ex:
        # Bloque except agregado para completar el try
        return jsonify({'mensaje': "Error: {}".format(ex), 'exito': False})

def pagina_no_encontrada(error):
    return "<h1>pagina no encontrada</h1>"


if __name__ == "__main__":
    app.config.from_object(config['development'])
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(host='0.0.0.0', port=5000)