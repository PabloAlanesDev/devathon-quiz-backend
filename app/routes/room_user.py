from http import HTTPStatus
from bson import ObjectId
from flask import jsonify, request
from flask_restx import Resource, abort
from mongoengine import ValidationError, DoesNotExist
from app.models.room import Room
from app.models.room_user import RoomUser


class RoomUserRoutes(Resource):
    def get(self, room_id):
        try:
            room = Room.objects.get(id=room_id)
            users = room.users
            if not users:
                abort(HTTPStatus.NOT_FOUND, message=f"Room {room_id} has not users")
            return jsonify([user.to_dict() for user in users])
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f"Room {room_id} was not found")

    def post(self, room_id):
        try:
            room = Room.objects.get(id=room_id)
            new_user = RoomUser(id=str(ObjectId()), **request.json)
            room.users.append(new_user)
            room.save()
            return jsonify(new_user.to_dict())
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f"Room {room_id} was not found")
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))
