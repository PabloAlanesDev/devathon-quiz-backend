import random

from flask import request
from flask_socketio import disconnect, emit
from mongoengine import DoesNotExist

from app.events import socketio
from app.models.quiz import Quiz, ResponseStatus
from app.models.room import Room, RoomStatus
from app.models.room_quiz import RoomQuizStatus, RoomQuiz
from app.models.room_user import RoomUserStatus, RoomUser

SCORE_QUIZ_CORRECT_DEFAULT = 10


@socketio.on('start_game')
def on_start():
    room_id = request.args.get('room_id')
    user_id = request.args.get('user_id')

    if not room_id or not user_id:
        disconnect()
        return

    print(f'User: {user_id} start game to Room: {room_id}\n')

    try:
        # Get room from DB
        room: Room = Room.objects.get(id=room_id, status=RoomStatus.CREATED,
                                      users__match={'id': user_id, 'role': 'owner'})

        # Update room status -> started in DB
        room.status = RoomStatus.STARTED

        # Select random quiz of room
        quiz_of_room = random.choice(room.quizzes)
        quiz: Quiz = Quiz.objects.get(id=quiz_of_room.quiz_id)

        # Update quiz status -> in_progress
        room.update_quiz_status(quiz_of_room.quiz_id, RoomQuizStatus.IN_PROGRESS)

        # Update all user status -> quiz_pending
        room.update_all_user_status(RoomUserStatus.QUIZ_PENDING)

        # Send Quiz
        emit('quiz_room', quiz.to_dict(hidden_response_status=True), to=room.id)

        print(f'Quiz: {quiz.id} published to room: {room_id}')

    except DoesNotExist:
        emit('message', f'User: {user_id} / Room: {room_id} Error: Not Found', to=room_id)
        disconnect()
    except Exception as e:
        emit('message', f'User: {user_id} Error: {str(e)}', to=room_id)
        disconnect()


@socketio.on('quiz_response')
def on_quiz_response(json):
    room_id = request.args.get('room_id')
    user_id = request.args.get('user_id')
    response_id = json.get('response_id')
    quiz_id = json.get('quiz_id')

    if not room_id or not user_id or not response_id or not quiz_id:
        disconnect()
        return

    print(f'User: {user_id} response Quiz: {quiz_id} in Room: {room_id}\n')

    try:
        # Get room from DB
        room: Room = Room.objects.get(id=room_id, status=RoomStatus.STARTED,
                                      users__match={'id': user_id})

        # Get quiz from DB
        quiz: Quiz = Quiz.objects.get(id=quiz_id)
        correct_response_ids = [r.id for r in quiz.responses if r.status == ResponseStatus.CORRECT]

        if response_id in correct_response_ids:
            # check response is correct -> +score -> user
            user: RoomUser = room.get_user(user_id)
            room.update_user_score(user_id, user.score + SCORE_QUIZ_CORRECT_DEFAULT)

        # Update user status -> quiz_done
        room.update_user_status(user_id, RoomUserStatus.QUIZ_DONE)

        # check if exist user status = pending
        any_user_pending = any([u.status == RoomUserStatus.QUIZ_PENDING for u in room.users])

        if not any_user_pending:
            # Update quiz status -> done
            room.update_quiz_status(quiz_id, RoomQuizStatus.DONE)

            # check if exist quiz status = pending
            any_quiz_pending = any([q.status == RoomQuizStatus.PENDING for q in room.quizzes])
            any_quiz_progress = any([q.status == RoomQuizStatus.IN_PROGRESS for q in room.quizzes])

            if not any_quiz_progress and any_quiz_pending:
                quizzes_pending = [q for q in room.quizzes if q.status == RoomQuizStatus.PENDING]

                # Select random Quiz of room
                quiz_of_room: RoomQuiz = random.choice(quizzes_pending)
                quiz: Quiz = Quiz.objects.get(id=quiz_of_room.quiz_id)

                # Update quiz status -> in_progress in DB
                room.update_quiz_status(quiz_of_room.id, RoomQuizStatus.IN_PROGRESS)

                # Update all user status -> quiz_pending in DB
                room.update_all_user_status(RoomUserStatus.QUIZ_PENDING)

                # Send quiz
                emit('quiz_room', quiz.to_dict(hidden_response_status=True), to=room.id)

                print(f'Quiz: {quiz.id} published to room: {room_id}')

            # check if all quiz status = done
            all_quizzes_done = all([q.status == RoomQuizStatus.DONE for q in room.quizzes])
            if all_quizzes_done:
                # Update room status -> finish in DB
                room.status = RoomStatus.FINISH
                room.save()

                # Get summary
                summary = [u.to_dict() for u in room.users]

                # Send summary of game
                emit('end_game', summary, to=room.id)

                print(f'Room: {room_id} end game\n')

    except DoesNotExist:
        emit('message', f'User: {user_id} / Room: {room_id} Error: Not Found', to=room_id)
        disconnect()
    except Exception as e:
        emit('message', f'User: {user_id} Error: {str(e)}', to=room_id)
        disconnect()
