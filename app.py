from app import app, socketio

if __name__ == '__main__':
    socketio.run(app, port=7878, host='0.0.0.0')
