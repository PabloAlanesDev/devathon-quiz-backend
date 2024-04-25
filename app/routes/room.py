from http import HTTPStatus

from flask_restx import Resource, abort
from mongoengine import ValidationError, DoesNotExist

from app.models.room import Room, ROOM_ID_COUNT_DIGITS
from flask import jsonify
from flask import request
from app.utils.generators import generate_random_digits


class RoomRoutes(Resource):
    def get(self, room_id=None):
        if room_id:
            try:
                room = Room.objects.get(id=room_id)
                return jsonify(room.to_dict())
            except DoesNotExist:
                abort(HTTPStatus.NOT_FOUND, message=f"Room {room_id} was not found")

        filter_with_quiz = request.args.get('with_quiz') in ['True', 'true'] or False
        filter_status = request.args.get('status')

        filter_query = dict()
        if filter_with_quiz:
            filter_query = dict(filter_query, **{'quiz_id__ne': None})
        if filter_status:
            filter_query = dict(filter_query, **{'status': filter_status})

        rooms_list = Room.objects(**filter_query)

        if not rooms_list:
            abort(HTTPStatus.NOT_FOUND, message="Rooms was not found")

        return jsonify([room.to_dict() for room in rooms_list])

    def post(self):
        room_id = generate_random_digits(ROOM_ID_COUNT_DIGITS)
        try:
            room = Room(**request.json, id=room_id)
            room.save()
            return jsonify(room.to_dict())
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

    def patch(self, room_id):
        try:
            room = Room.objects.get(id=room_id)
            room.update(**request.json)
            return jsonify(message=f'Room {room_id} was updated')
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f"Room {room_id} was not found")
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

    def delete(self, room_id):
        try:
            room = Room.objects.get(id=room_id)
            room.delete()
            return jsonify(message=f'Room {room_id} was deleted')
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f"Room {room_id} was not found")
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))
