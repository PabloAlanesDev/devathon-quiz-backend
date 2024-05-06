from enum import Enum
from mongoengine import StringField, EnumField, EmbeddedDocument


class RoomQuizStatus(Enum):
    DONE = 'done'
    IN_PROGRESS = 'in_progress'
    PENDING = 'pending'


class RoomQuiz(EmbeddedDocument):
    id = StringField(required=True)
    quiz_id = StringField(required=True)
    status = EnumField(RoomQuizStatus, default=RoomQuizStatus.PENDING)

    def to_dict(self):
        return {
            'id': str(self.id),
            'quiz_id': str(self.quiz_id),
            'status': self.status.value
        }
