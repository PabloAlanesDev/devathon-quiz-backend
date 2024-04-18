import os

from dotenv import load_dotenv
from flask import Flask
from flask_socketio import SocketIO, join_room, leave_room, send

from config.mongodb import mongo
from routes.quiz import quiz

load_dotenv()

app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo.init_app(app)

app.register_blueprint(quiz, url_prefix='/quiz')
socketio = SocketIO(app, cors_allowed_origins='*')


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room_id']
    join_room(room)
    send(username + ' has entered the room.', to=room)


@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room_id']
    leave_room(room)
    send(username + ' has left the room.', to=room)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
