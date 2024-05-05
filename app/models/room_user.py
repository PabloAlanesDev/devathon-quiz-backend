from enum import Enum
from mongoengine import StringField, EnumField, FloatField, EmbeddedDocument


class RoomUserStatus(Enum):
    UNKNOWN = 'unknown'
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'
    QUIZ_PENDING = 'quiz_pending'
    QUIZ_DONE = 'quiz_done'


class RoomUserRole(Enum):
    OWNER = 'owner'
    INVITED = 'invited'


class RoomUser(EmbeddedDocument):
    id = StringField(required=True)
    name = StringField(max_length=20, required=True)
    status = EnumField(RoomUserStatus, default=RoomUserStatus.UNKNOWN)
    role = EnumField(RoomUserRole, default=RoomUserRole.INVITED)
    score = FloatField(default=0)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'role': self.role.value,
            'status': self.status.value,
            'score': self.score
        }
