from flask_socketio import SocketIO

socketio = SocketIO()

from . import room, game # noqa
