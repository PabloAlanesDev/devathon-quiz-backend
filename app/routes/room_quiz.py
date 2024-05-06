from http import HTTPStatus
import random

from bson import ObjectId
from flask_restx import Resource, abort
from mongoengine import ValidationError, DoesNotExist
from app.models.quiz import Quiz
from app.models.room import Room, ROOM_QUIZ_COUNT_DEFAULT
from flask import jsonify
from flask import request

from app.models.room_quiz import RoomQuiz


class RoomQuizRoutes(Resource):

    def get(self, room_id):
        try:
            room = Room.objects.get(id=room_id)
            quizzes = room.quizzes
            if not quizzes:
                abort(HTTPStatus.NOT_FOUND, message=f"Quizzes from room {room_id} was not found")
            return jsonify([q.to_dict() for q in quizzes])
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f"Room {room_id} was not found")

    def post(self, room_id):
        try:
            room = Room.objects.get(id=room_id)
            topics = request.json.get('topics')

            quizzes_of_topics = Quiz.objects.filter(topic_id__in=topics)

            if not quizzes_of_topics:
                abort(HTTPStatus.NOT_FOUND, message=f"Quizzes from room {room_id} was not found")

            quiz_ids = [q.id for q in quizzes_of_topics]

            random.shuffle(quiz_ids)

            for quiz_id in quiz_ids[:ROOM_QUIZ_COUNT_DEFAULT]:
                room_quiz = RoomQuiz(id=str(ObjectId()), quiz_id=str(quiz_id))
                room.quizzes.append(room_quiz)

            room.save()

            return jsonify([q.to_dict() for q in room.quizzes])
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f"Room {room_id} was not found")
