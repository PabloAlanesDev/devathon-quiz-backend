from enum import Enum
from bson import ObjectId
from mongoengine import (StringField, EnumField, EmbeddedDocument,
                         EmbeddedDocumentListField, Document)


class ResponseStatus(Enum):
    CORRECT = 'correct'
    INCORRECT = 'incorrect'


class Response(EmbeddedDocument):
    id = StringField(required=True)
    text = StringField(required=True)
    status = EnumField(ResponseStatus, default=ResponseStatus.INCORRECT)

    def to_dict(self, hidden_status=False):
        if hidden_status:
            return {
                'id': self.id,
                'text': self.text
            }
        return {
            'id': self.id,
            'text': self.text,
            'status': self.status.value
        }


class Quiz(Document):
    question = StringField(required=True)
    topic_id = StringField(required=True)
    responses = EmbeddedDocumentListField(Response)

    def to_dict(self, hidden_response_status=False):
        return {
            'id': str(self.id),
            'question': self.question,
            'topic_id': str(self.topic_id),
            'responses': [r.to_dict(hidden_response_status) for r in self.responses]
        }

    def save(self):
        # auto generate id for the responses
        for r in self.responses:
            r.id = str(ObjectId())
        super().save()
