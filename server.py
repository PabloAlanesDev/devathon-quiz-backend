import os

from dotenv import load_dotenv
from flask import Flask
from flask_socketio import SocketIO

from config.mongodb import mongo
from routes.quiz import quiz

load_dotenv()

app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI')
mongo.init_app(app)

app.register_blueprint(quiz, url_prefix='/quiz')
socketio = SocketIO(app, cors_allowed_origins='*')


@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
