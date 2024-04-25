from enum import Enum
from mongoengine import Document, StringField, EnumField, FloatField

from app.models.room import ROOM_ID_COUNT_DIGITS


class UserStatus(Enum):
    UNKNOWN = 'unknown'
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'


class UserRole(Enum):
    OWNER = 'owner'
    INVITED = 'invited'


class User(Document):
    name = StringField(max_length=20, required=True)
    room_id = StringField(max_length=ROOM_ID_COUNT_DIGITS)
    status = EnumField(UserStatus, default=UserStatus.UNKNOWN)
    role = EnumField(UserRole, default=UserRole.INVITED)
    score = FloatField(default=0)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'room_id': self.room_id,
            'role': self.role.value,
            'status': self.status.value,
            'score': self.score
        }
