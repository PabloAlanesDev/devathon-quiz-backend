from app.app import create_app, init_db, init_socketio
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    app = create_app()
    mongo = init_db(app)
    socketio = init_socketio(app)
    socketio.run(app, host='0.0.0.0', debug=True, allow_unsafe_werkzeug=True)
