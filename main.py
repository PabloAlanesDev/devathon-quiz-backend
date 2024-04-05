from flask import Flask, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Definimos un endpoint para la ruta '/datos'


@app.route('/', methods=['GET'])
def obtener_datos():
    datos = {
        'nombre': 'Juan',
        'edad': 30,
        'ciudad': 'Madrid'
    }
    return jsonify(datos)


if __name__ == '__main__':
    socketio.run(app, debug=True)
