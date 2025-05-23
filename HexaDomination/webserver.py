from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}  # code_salon: [sid1, sid2]

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on('create_room')
def on_create(data):
    code = data['code']
    rooms[code] = [request.sid]
    join_room(code)
    emit('room_created', {'code': code})

@socketio.on('join_room')
def on_join(data):
    code = data['code']
    if code in rooms and len(rooms[code]) < 2:
        rooms[code].append(request.sid)
        join_room(code)
        emit('room_joined', {'code': code}, room=code)
    else:
        emit('join_failed', {'reason': 'Salon plein ou inexistant'})

@socketio.on('game_message')
def on_game_message(data):
    code = data['code']
    emit('game_message', data, room=code)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)