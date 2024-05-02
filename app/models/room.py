from enum import Enum
from bson import ObjectId
from mongoengine import StringField, FloatField, EmbeddedDocument, IntField, EnumField, Document, EmbeddedDocumentListField

from app.models.user import User

ROOM_ID_COUNT_DIGITS = 6


class RoomStatus(Enum):
    CREATED = 'created'
    STARTED = 'started'
    FULL = 'full'
    EMPTY = 'empty'
    FINISH = 'finish'

class QuizRoomStatus(Enum):
    DONE = 'done'
    IN_PROGRESS = 'in_progress'
    PENDING = 'pending'


class QuizRoom(EmbeddedDocument):
    id = StringField(required=True)
    quiz_id = StringField(required=True)
    status = EnumField(QuizRoomStatus, default=QuizRoomStatus.PENDING)

    def to_dict(self):
        return {
            'id': str(self.id),
            'quiz_id': str(self.quiz_id),
            'status': self.status.value
        }


class UserRoomStatus(Enum):
    UNKNOWN = 'unknown'
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'
    QUIZ_PENDING = 'quiz_pending'
    QUIZ_DONE = 'quiz_done'



class UserRoomRole(Enum):
    OWNER = 'owner'
    INVITED = 'invited'


class UserRoom(EmbeddedDocument):
    id = StringField(required=True)
    name = StringField(max_length=20, required=True)
    status = EnumField(UserRoomStatus, default=UserRoomStatus.UNKNOWN)
    role = EnumField(UserRoomRole, default=UserRoomRole.INVITED)
    score = FloatField(default=0)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'role': self.role.value,
            'status': self.status.value,
            'score': self.score
        }



class Room(Document):
    id = StringField(max_length=ROOM_ID_COUNT_DIGITS, required=True, primary_key=True)
    status = EnumField(RoomStatus, default=RoomStatus.CREATED)
    quizzes = EmbeddedDocumentListField(QuizRoom)
    users = EmbeddedDocumentListField(UserRoom)

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

    def add_user(self, user_data):
        new_user = UserRoom(id=str(ObjectId()), **user_data)
        self.users.append(new_user)
        super().save()
        return new_user

    def update_user(self, user_id, user_data):
        current_user = list(filter(lambda x: x.id == user_id, self.users))[0]
        new_data = {**current_user.to_dict(), **user_data}
        new_user = UserRoom(**new_data)
        self.users = list(filter(lambda x: x.id != user_id, self.users))
        self.users.append(new_user)
        super().save()
    
    def update_users_status(self, status):
        for u in self.users:
            u.status = status        
        super().save()

    def remove_user(self, user_id):
        self.users = list(filter(lambda x: x.id != user_id, self.users))
        super().save()

    def add_quizzes(self, quizzes):
        for q in quizzes:
            qr = QuizRoom(id=str(ObjectId()), quiz_id=str(q))
            self.quizzes.append(qr)
        super().save()
        return self.quizzes

    def update_quiz(self, quiz_id, quiz_data):
        current_quiz = list(filter(lambda x: x.quiz_id == quiz_id, self.quizzes))[0]
        new_data = {**current_quiz.to_dict(), **quiz_data}
        new_quiz = QuizRoom(**new_data)
        self.quizzes = list(filter(lambda x: x.quiz_id != quiz_id, self.quizzes))
        self.quizzes.append(new_quiz)
        super().save()