from flask import Blueprint
from flask import request
from utils.parsers import parse_json
from utils.generators import generate_random_digits

rooms = Blueprint('rooms', __name__)

ROOM_ID_COUNT_DIGITS = 6
QUIZ_COUNT_DEFAULT = 5


class UserRole:
    OWNER = 'owner'
    INVITED = 'invited'


class UserStatus:
    UNKNOWN = 'unknown'
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'


class RoomStatus:
    CREATED = 'created'
    STARTED = 'started'
    FULL = 'full'
    EMPTY = 'empty'


@rooms.route('/', methods=['POST'])
def create_room():
    owner = request.json.get('owner')
    quiz_id = request.json.get('quiz_id')
    quiz_count = request.json.get('quiz_count')

    room_id = generate_random_digits(ROOM_ID_COUNT_DIGITS)

    user_data = {
        'role': UserRole.OWNER,
        'name': owner,
        'score': 0,
        'status': UserStatus.UNKNOWN
    }

    user_saved = mongo.db.users.insert_one(parse_json(user_data))

    data = {
        'id': room_id,
        'owner': owner,
        'quiz_id': quiz_id,
        'quiz_count': quiz_count or QUIZ_COUNT_DEFAULT,
        'status': RoomStatus.CREATED,
        'users': [str(user_saved.inserted_id)]
    }

    mongo.db.rooms.insert_one(parse_json(data))

    return data


# TODO: Fix circular dependencies with pymongo and flask app
from server import mongo # noqa
