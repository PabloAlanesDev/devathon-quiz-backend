from flask_socketio import disconnect, join_room, emit, leave_room
from app.events import socketio
from app.models.quiz import Quiz
from app.models.room import Room, RoomStatus, UserRoomStatus
from app.models.user import User, UserStatus
from mongoengine import ValidationError, DoesNotExist
from flask import request
import random


@socketio.on('connect')
def on_connect():
    room_id = request.args.get('room_id')
    user_id = request.args.get('user_id')

    print(f'\nUser: {user_id} connect in {room_id}\n')

    try:
        # Get room from DB
        room = Room.objects.get(id=room_id, status=RoomStatus.CREATED, users__match={'id': user_id})

        # update user in DB
        room.update_user(user_id, {'status': 'connect'})

        # Join socket connection to room
        join_room(room.id)

        # Get users of room
        room_users = [x.to_dict() for x in room.users if x.status.value == 'connect']

        emit('message', user_id + ' has entered the room.', to=room.id)
        emit('room_users', room_users, to=room.id)

    except DoesNotExist:
        emit('message', 'Not Found')
        disconnect()
    except ValidationError:
        emit('message', 'Bad Request')
        disconnect()
    except Exception as e:
        emit('message', str(e))
        disconnect()


@socketio.on('disconnect')
def on_disconnect():
    room_id = request.args.get('room_id')
    user_id = request.args.get('user_id')

    print(f'\nUser: {user_id} disconnect in {room_id}\n')

    if not room_id or not user_id:
        disconnect()
        return

    try:
        # Get room from DB
        room = Room.objects.get(id=room_id, users__match={'id': user_id})

        # update user in DB
        room.update_user(user_id, {'status': 'disconnect'})

        # Leave socket connection to room
        leave_room(room.id)

        # Get users of room
        room_users = [x.to_dict() for x in room.users if x.status.value != 'disconnect']

        if room_users:
            emit('message', user_id + ' has entered the room.', to=room.id)
            emit('room_users', room_users, to=room.id)
        else:
            # remove room in DB
            room.delete()
        
        disconnect()


    except DoesNotExist:
        emit('message', 'Not Found')
        disconnect()
    except ValidationError:
        emit('message', 'Bad Request')
        disconnect()
    except Exception as e:
        emit('message', str(e))
        disconnect()



@socketio.on('leave_room')
def on_leave():
    room_id = request.args.get('room_id')
    user_id = request.args.get('user_id')

    print(f'\nUser: {user_id} leave room in {room_id}\n')

    try:
        # Get room from DB
        room = Room.objects.get(id=room_id, status=RoomStatus.FINISH, users__match={'id': user_id})

        # update user in DB
        room.remove_user(user_id)

        # Leave socket connection to room
        leave_room(room.id)

        # Get users of room
        room_users = [x.to_dict() for x in room.users if x.status.value != 'disconnect']

        if room_users:
            emit('message', user_id + ' has entered the room.', to=room.id)
            emit('room_users', room_users, to=room.id)
        else:
            # remove room in DB
            room.delete()
        
        disconnect()

    except DoesNotExist:
        emit('message', 'Not Found')
        disconnect()
    except ValidationError:
        emit('message', 'Bad Request')
        disconnect()
    except Exception as e:
        emit('message', str(e))
        disconnect()



@socketio.on('start_game')
def on_start():
    room_id = request.args.get('room_id')
    user_id = request.args.get('user_id')

    print(f'\nUser: {user_id} start room {room_id}\n')

    try:
        # Get room from DB
        room = Room.objects.get(id=room_id, status=RoomStatus.CREATED, users__match={'id': user_id, 'role': 'owner'})

        room.status = RoomStatus.STARTED

        quiz = random.choice(room.quizzes)
        quiz_data = Quiz.objects.get(id=quiz.quiz_id)

        room.update_quiz(quiz.quiz_id, {'status': 'in_progress'})
        room.update_users_status(UserRoomStatus.QUIZ_PENDING)
        emit('quiz_room', quiz_data.to_dict(True), to=room.id)
        print(f'\nRoom: {room_id} publish quiz {quiz.quiz_id}\n')

    except DoesNotExist:
        emit('message', 'Not Found')
        disconnect()
    except ValidationError:
        emit('message', 'Bad Request')
        disconnect()

    except Exception as e:
        emit('message', str(e))
        disconnect()


@socketio.on('quiz_response')
def on_quiz(json):
    room_id = request.args.get('room_id')
    user_id = request.args.get('user_id')

    response_id = json.get('response_id')
    quiz_id = json.get('quiz_id')

    print(f'\nRoom: {room_id} User: {user_id} response quiz in {quiz_id}\n')

    try:
        # Get room from DB
        room = Room.objects.get(id=room_id, status=RoomStatus.STARTED, users__match={'id': user_id})

        quiz = Quiz.objects.get(id=quiz_id)
        responses_correct = [r.id for r in quiz.responses if r.status.value == 'correct']

        if response_id in responses_correct:
            user = list(filter(lambda x: x.id == user_id, room.users))[0]
            room.update_user(user_id, {'score': user.score + 10, 'status': 'quiz_done'})
        else:
            room.update_user(user_id, {'status': 'quiz_done'})
    
        user_pending = [u for u in room.users if u.status.value == 'quiz_pending']
        
        any_user_pending = any([u.status.value == 'quiz_pending' for u in room.users])
        any_quiz_pending = any([q.status.value == 'pending' for q in room.quizzes if q.quiz_id != quiz_id])

        any_quizzes_progress = any([q.status.value == 'in_progress' for q in room.quizzes])
        all_quizzes_done = all([q.status.value == 'done' for q in room.quizzes])


        if not any_user_pending:
            room.update_quiz(quiz_id, {'status': 'done'})

            if any_quiz_pending:
                quizzes_pending = [q for q in room.quizzes if q.status.value == 'pending']
                quiz = random.choice(quizzes_pending)
                quiz_data = Quiz.objects.get(id=quiz.quiz_id)

                room.update_quiz(quiz.quiz_id, {'status': 'in_progress'})
                room.update_users_status(UserRoomStatus.QUIZ_PENDING)
                emit('quiz_room', quiz_data.to_dict(True), to=room.id)
                print(f'\nRoom: {room_id} publish quiz {quiz.quiz_id}\n')

            
            all_quizzes_done = all([q.status.value == 'done' for q in room.quizzes])

            if all_quizzes_done:
                room.status = RoomStatus.FINISH
                room.save()
                summary = [u.to_dict() for u in room.users]
                emit('end_game', summary, to=room.id)
                print(f'\nRoom: {room_id} end game\n')

    except DoesNotExist:
        emit('message', 'Not Found')
        disconnect()

    except ValidationError:
        emit('message', 'Bad Request')
        disconnect()

    except Exception as e:
        emit('message', str(e))
        disconnect()

