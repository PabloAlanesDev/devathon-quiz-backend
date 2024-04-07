from flask import Flask, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')


@app.route('/', methods=['GET'])
def example():
    data = {
        'name': 'Juan',
        'age': 30,
        'city': 'Madrid'
    }
    return jsonify(data)


@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
