from enum import Enum
from mongoengine import EmbeddedDocument, StringField, EnumField, FloatField


class UserStatus(Enum):
    UNKNOWN = 'unknown'
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'


class UserRole(Enum):
    OWNER = 'owner'
    INVITED = 'invited'


class User(EmbeddedDocument):
    id = StringField(required=True)
    name = StringField(max_length=20, required=True)
    status = EnumField(UserStatus, default=UserStatus.UNKNOWN)
    role = EnumField(UserRole, default=UserRole.INVITED)
    score = FloatField(default=0)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'role': self.role.value,
            'status': self.status.value,
            'score': self.score
        }
