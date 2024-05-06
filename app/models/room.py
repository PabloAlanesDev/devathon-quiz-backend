from enum import Enum
from bson import ObjectId
from mongoengine import StringField, EnumField, Document, EmbeddedDocumentListField
from app.models.room_quiz import RoomQuiz, RoomQuizStatus
from app.models.room_user import RoomUser, RoomUserStatus

ROOM_ID_COUNT_DIGITS = 6
ROOM_QUIZ_COUNT_DEFAULT = 5


class RoomStatus(Enum):
    CREATED = 'created'
    STARTED = 'started'
    FULL = 'full'
    EMPTY = 'empty'
    FINISH = 'finish'


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

    def save(self):
        for u in self.users:
            if not u.id:
                u.id = str(ObjectId())
        for q in self.quizzes:
            if not q.id:
                q.id = str(ObjectId())
        super().save()

    def get_user(self, user_id: str) -> RoomUser:
        for user in self.users:
            if user.id == user_id:
                return user

    def update_all_user_status(self, status: RoomUserStatus):
        for user in self.users:
            user.status = status
        super().save()

    def update_user_status(self, user_id: str, status: RoomUserStatus):
        for user in self.users:
            if user.id == user_id:
                user.status = status
                break
        super().save()

    def update_user_score(self, user_id: str, score: float):
        for user in self.users:
            if user.id == user_id:
                user.score = score
                break
        super().save()

    def remove_user(self, user_id: str):
        self.users = list(filter(lambda x: x.id != user_id, self.users))
        super().save()

    def update_quiz_status(self, quiz_id: str, status: RoomQuizStatus):
        for quiz in self.quizzes:
            if quiz.quiz_id == quiz_id:
                quiz.status = status
                break
        super().save()
