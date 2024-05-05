from enum import Enum
from mongoengine import StringField, EnumField, Document, EmbeddedDocumentListField
from app.models.room_quiz import RoomQuiz
from app.models.room_user import RoomUser

ROOM_ID_COUNT_DIGITS = 6


class RoomStatus(Enum):
    CREATED = 'created'
    STARTED = 'started'
    FULL = 'full'
    EMPTY = 'empty'


class Room(Document):
    id = StringField(max_length=ROOM_ID_COUNT_DIGITS, required=True, primary_key=True)
    status = EnumField(RoomStatus, default=RoomStatus.CREATED)
    users = EmbeddedDocumentListField(RoomUser)
    quizzes = EmbeddedDocumentListField(RoomQuiz)

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status.value,
            'quizzes': [q.to_dict() for q in self.quizzes],
            'users': [u.to_dict() for u in self.users]
        }
