from http import HTTPStatus
from flask import jsonify
from flask import request
from flask_restx import Resource, abort
from mongoengine import ValidationError

from app.models.quiz import Quiz


class TopicQuizRoutes(Resource):
    def get(self, topic_id):
        quizzes = Quiz.objects(topic_id=topic_id)

        if not quizzes:
            abort(HTTPStatus.NOT_FOUND, message=f'Quizzes from topic:{topic_id} was not found')

        return jsonify([q.to_dict() for q in quizzes])

    def post(self, topic_id):
        quizzes = request.json

        if not isinstance(quizzes, list):
            abort(HTTPStatus.BAD_REQUEST, message='Request not contain list of elements')

        count_quizzes = len(quizzes)

        try:
            for q in quizzes:
                quiz = Quiz(topic_id=topic_id, **q)
                quiz.save()

            quizzes_in_db = Quiz.objects(topic_id=topic_id)
            count_quizzes_in_db = len(quizzes_in_db)

            if not quizzes_in_db:
                abort(HTTPStatus.FORBIDDEN, message='Quizzes was not created')
            if count_quizzes != count_quizzes_in_db:
                abort(HTTPStatus.FORBIDDEN, message='Any Quiz was not created')

            return jsonify([q.to_dict() for q in quizzes_in_db])

        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))
