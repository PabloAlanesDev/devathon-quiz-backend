from enum import Enum
from mongoengine import StringField, IntField, EnumField, Document

ROOM_ID_COUNT_DIGITS = 6


class RoomStatus(Enum):
    CREATED = 'created'
    STARTED = 'started'
    FULL = 'full'
    EMPTY = 'empty'


class Room(Document):
    id = StringField(max_length=ROOM_ID_COUNT_DIGITS, required=True, primary_key=True)
    owner = StringField(max_length=20, required=True)
    quiz_id = StringField(max_length=50, required=False)
    quiz_count = IntField(required=False, default=5)
    status = EnumField(RoomStatus, default=RoomStatus.CREATED)

    def to_dict(self):
        return {
            'id': self.id,
            'owner': self.owner,
            'quiz_id': self.quiz_id,
            'quiz_count': self.quiz_count,
            'status': self.status.value
        }
