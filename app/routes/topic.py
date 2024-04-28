from http import HTTPStatus
from flask import jsonify
from flask import request
from flask_restx import Resource, abort
from mongoengine import ValidationError, DoesNotExist, NotUniqueError

from app.models.topic import Topic


class TopicRoutes(Resource):
    def get(self, topic_id=None):
        if topic_id:
            try:
                topic = Topic.objects.get(id=topic_id)
                return jsonify(topic.to_dict())
            except DoesNotExist:
                abort(HTTPStatus.NOT_FOUND, message=f'Topic {topic_id} was not found')

        topics_list = Topic.objects()

        if not topics_list:
            abort(HTTPStatus.NOT_FOUND, message='Topics was not found')

        return jsonify([topic.to_dict() for topic in topics_list])

    def post(self):
        try:
            topic = Topic(**request.json)
            topic.save()
            return jsonify(topic.to_dict())
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))
        except NotUniqueError:
            abort(HTTPStatus.CONFLICT, message='Object already exist')

    def patch(self, topic_id):
        try:
            topic = Topic.objects.get(id=topic_id)
            topic.update(**request.json)
            return jsonify(message=f'Topic {topic_id} was updated')
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f"Topic {topic_id} was not found")
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

    def delete(self, topic_id):
        try:
            topic = Topic.objects.get(id=topic_id)
            topic.delete()
            return jsonify(message=f'Topic {topic_id} was deleted')
        except DoesNotExist:
            abort(HTTPStatus.NOT_FOUND, message=f"Topic {topic_id} was not found")
        except ValidationError as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))
