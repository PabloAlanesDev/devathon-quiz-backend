from http import HTTPStatus

from flask_restx import Resource, abort
from mongoengine import ValidationError, DoesNotExist

from flask import jsonify
from flask import request

from app.models.user import User


class UserRoutes(Resource):
    def get(self, user_id=None):
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                return jsonify(user.to_dict())
            except DoesNotExist:
                abort(HTTPStatus.NOT_FOUND, message=f"User {user_id} was not found")

        filter_status = request.args.get('status')
        filter_role = request.args.get('role')
        filter_room = request.args.get('room')

        filter_query = dict()
        if filter_role:
            filter_query = dict(filter_query, **{'role': filter_role})
        if filter_status:
            filter_query = dict(filter_query, **{'status': filter_status})
        if filter_room:
            filter_query = dict(filter_query, **{'room_id': filter_room})

        users_list = User.objects(**filter_query)

        if not users_list:
            abort(HTTPStatus.NOT_FOUND, message="Users was not found")

        return jsonify([user.to_dict() for user in users_list])

    def post(self):
        try:
            user = User(**request.json)
            user.save()
            return jsonify(user.to_dict())
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

    def patch(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.update(**request.json)
            return jsonify(message=f'User {user_id} was updated')
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f"User {user_id} was not found")
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

    def delete(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.delete()
            return jsonify(message=f'User {user_id} was deleted')
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f"User {user_id} was not found")
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))
