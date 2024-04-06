from flask import Flask, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route('/', methods=['GET'])
def example():
    data = {
        'name': 'Juan',
        'age': 30,
        'city': 'Madrid'
    }
    return jsonify(data)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
