from flask_socketio import disconnect, join_room, emit, leave_room
from app.events import socketio
from app.models.room import Room, RoomStatus
from mongoengine import DoesNotExist
from flask import request

from app.models.room_user import RoomUserStatus


@socketio.on('connect')
def on_connect():
    room_id = request.args.get('room_id')
    user_id = request.args.get('user_id')

    if not room_id or not user_id:
        disconnect()
        return

    print(f'User: {user_id} connect to Room: {room_id}\n')

    try:
        # Get room from DB
        room: Room = Room.objects.get(id=room_id, status=RoomStatus.CREATED,
                                      users__match={'id': user_id})

        # Update user status -> connect in DB
        room.update_user_status(user_id, RoomUserStatus.CONNECT)

        # Join to socket room connection
        join_room(room.id)

        # Get all users from room
        room_users = [u.to_dict() for u in room.users if u.status == RoomUserStatus.CONNECT]

        emit('message', f'User:{user_id} has joined the room', to=room.id)

        # Send users
        emit('room_users', room_users, to=room.id)

    except DoesNotExist:
        emit('message', f'User: {user_id} / Room: {room_id} Error: Not Found', to=room_id)
        disconnect()
    except Exception as e:
        emit('message', f'User: {user_id} Error: {str(e)}', to=room_id)
        disconnect()


@socketio.on('disconnect')
def on_disconnect():
    room_id = request.args.get('room_id')
    user_id = request.args.get('user_id')

    if not room_id or not user_id:
        disconnect()
        return

    print(f'User: {user_id} disconnect from Room: {room_id}\n')

    try:
        # Get room from DB
        room = Room.objects.get(id=room_id, users__match={'id': user_id})

        # Update user status -> disconnect in DB
        room.update_user_status(user_id, RoomUserStatus.DISCONNECT)

        # Leave socket connection of room
        leave_room(room.id)

        # Get users from room
        room_users = [u.to_dict() for u in room.users if u.status != RoomUserStatus.DISCONNECT]

        if room_users:
            emit('message', f'User:{user_id} has disconnected of the room', to=room.id)
            # Send users
            emit('room_users', room_users, to=room.id)
        else:
            # Remove room
            room.delete()

        disconnect()

    except DoesNotExist:
        emit('message', f'User: {user_id} / Room: {room_id} Error: Not Found', to=room_id)
        disconnect()
    except Exception as e:
        emit('message', f'User: {user_id} Error: {str(e)}', to=room_id)
        disconnect()


@socketio.on('leave_room')
def on_leave():
    room_id = request.args.get('room_id')
    user_id = request.args.get('user_id')

    if not room_id or not user_id:
        disconnect()
        return

    print(f'User: {user_id} leave from Room: {room_id}\n')

    try:
        # Get room from DB
        room: Room = Room.objects.get(id=room_id, status=RoomStatus.FINISH,
                                      users__match={'id': user_id})

        # Remove user from room
        room.remove_user(user_id)

        # Leave socket connection of room
        leave_room(room.id)

        # Get users from room
        room_users = [u.to_dict() for u in room.users if u.status != RoomUserStatus.DISCONNECT]

        if room_users:
            emit('message', f'User:{user_id} has leave of the room', to=room.id)
            # Send users
            emit('room_users', room_users, to=room.id)
        else:
            # Remove room
            room.delete()

        disconnect()

    except DoesNotExist:
        emit('message', f'User: {user_id} / Room: {room_id} Error: Not Found', to=room_id)
        disconnect()
    except Exception as e:
        emit('message', f'User: {user_id} Error: {str(e)}', to=room_id)
        disconnect()
