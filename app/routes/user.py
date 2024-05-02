from http import HTTPStatus

from bson import ObjectId
from flask_restx import Resource, abort
from mongoengine import ValidationError, DoesNotExist

from flask import jsonify
from flask import request

from app.models.room import Room, UserRoom
from app.models.user import User


class UserRoutes(Resource):
    def get(self, room_id, user_id=None):
        if user_id:
            try:
                room = Room.objects.get(id=room_id, users__match={'id': user_id})
                user = [u for u in room.users if u.id == user_id]
                return jsonify(user[0].to_dict())
            except DoesNotExist:
                abort(HTTPStatus.NOT_FOUND, message=f"User {user_id} was not found")

        room = Room.objects.get(id=room_id)
        users = room.users

        if not users:
            abort(HTTPStatus.NOT_FOUND, message="Users was not found")

        return jsonify([user.to_dict() for user in users])

    def post(self, room_id, user_id=None):
        try:
            room = Room.objects.get(id=room_id)
            user = room.add_user(request.json)
            return jsonify(user.to_dict())
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

    def patch(self, room_id, user_id):
        try:
            room = Room.objects.get(id=room_id)
            room.update_user(user_id, request.json)
            return jsonify(message=f'User {user_id} was updated')
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f"User {user_id} was not found")
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

    def delete(self, room_id, user_id):
        try:
            room = Room.objects.get(id=room_id)
            room.remove_user(user_id)
            return jsonify(message=f'User {user_id} was deleted')
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f"User {user_id} was not found")
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))
