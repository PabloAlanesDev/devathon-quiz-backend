from flask import Flask
from flask_mongoengine import MongoEngine
from flask_restx import Api

from app.config.mongodb import mongo_config
from app.routes.swagger import swagger
from app.routes.room import RoomRoutes
from app.routes.user import UserRoutes

mongo = MongoEngine()
api = Api()


def create_app():
    app = Flask(__name__)
    app.register_blueprint(swagger, url_prefix='/swagger')
    api.add_resource(RoomRoutes, '/api/rooms/', '/api/rooms/<string:room_id>')
    api.add_resource(UserRoutes, '/api/users/', '/api/users/<string:user_id>')
    api.init_app(app)
    return app


def init_db(app):
    app.config["MONGODB_SETTINGS"] = [mongo_config]
    mongo.init_app(app)
    return mongo


def init_socketio(app):
    from app.events.room import socketio
    socketio.init_app(app, cors_allowed_origins='*')
    return socketio
