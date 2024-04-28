from http import HTTPStatus
from flask import jsonify
from flask import request
from flask_restx import Resource, abort
from mongoengine import ValidationError, DoesNotExist, NotUniqueError
from pymongo.errors import DuplicateKeyError

from app.models.quiz import Quiz


class QuizRoutes(Resource):
    def get(self, quiz_id=None):
        if quiz_id:
            try:
                quiz = Quiz.objects.get(id=quiz_id)
                return jsonify(quiz.to_dict())
            except DoesNotExist:
                abort(HTTPStatus.NOT_FOUND, message=f'Quiz {quiz_id} was not found')

        filter_topic = request.args.get('topic')
        hidden_response_status = (request.args.get('hidden_response_status') in ['True', 'true']
                                  or False)

        filter_query = dict()
        if filter_topic:
            filter_query = dict(filter_query, **{'topic_id': filter_topic})

        quizzes_list = Quiz.objects(**filter_query)

        if not quizzes_list:
            abort(HTTPStatus.NOT_FOUND, message='Quizzes was not found')

        return jsonify([quiz.to_dict(hidden_response_status) for quiz in quizzes_list])

    def post(self):
        try:
            quiz = Quiz(**request.json)
            quiz.save()
            return jsonify(quiz.to_dict())
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))
        except (NotUniqueError, DuplicateKeyError):
            abort(HTTPStatus.CONFLICT, message='Object already exist')

    def patch(self, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            quiz.update(**request.json)
            return jsonify(message=f'Quiz {quiz_id} was updated')
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f'Quiz {quiz_id} was not found')
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

    def delete(self, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
            quiz.delete()
            return jsonify(message=f'Quiz {quiz_id} was deleted')
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f'Quiz {quiz_id} was not found')
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))
