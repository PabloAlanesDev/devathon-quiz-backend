from flask_socketio import disconnect, join_room, emit, leave_room
from app.events import socketio
from app.models.room import Room, RoomStatus
from app.models.user import User, UserStatus
from mongoengine import ValidationError, DoesNotExist


@socketio.on('join_room')
def on_join(json):
    try:
        # Get user from DB
        user = User.objects.get(id=json.get('user_id'))

        # Get room from DB
        room = Room.objects.get(id=json.get('room_id'), status=RoomStatus.CREATED)

        # Join socket connection to room
        join_room(room.id)

        # Update user
        user.update(room_id=room.id, status=UserStatus.CONNECT)

        # Get users of room
        room_users = [x.to_dict() for x in User.objects(room_id=room.id)]

        emit('message', user.name + ' has entered the room.', to=room.id)
        emit('room_users', room_users, to=room.id)

    except DoesNotExist:
        emit('message', 'Not Found')
        disconnect()
    except ValidationError:
        emit('message', 'Bad Request')
        disconnect()
    except Exception as e:
        emit('message', str(e))


@socketio.on('leave_room')
def on_leave(json):
    try:
        # Get user from DB and update
        user = User.objects.get(**json)
        user.update(room_id=None, status=UserStatus.DISCONNECT)

        # Get room from DB
        room = Room.objects.get(id=user.room_id)

        # Leave socket connection from room
        leave_room(user.room_id)

        # Get users from room
        room_users = [x.to_dict() for x in User.objects(room_id=room.id)]

        emit('message', user.name + ' has left the room.', to=room.id)
        emit('room_users', room_users, to=room.id)

        # disconnect socket connection
        disconnect()

    except DoesNotExist:
        emit('message', 'Not Found')
    except Exception as e:
        emit('message', str(e))
