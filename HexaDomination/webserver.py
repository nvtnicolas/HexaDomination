from flask import Flask, render_template, request, redirect, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
from database import init_db, add_user, check_user, get_user_games, add_friend, get_friends, save_game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

rooms = {}  # code_salon: {'players': [pseudo1, pseudo2], 'visible': True/False}
queue = []  # Liste des joueurs en attente : [{pseudo, ip, date, sid}]
waiting_rooms = {}  # code: [{'pseudo':..., 'ready':False, 'sid':...}, ...]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/game")
def game():
    return render_template("game.html")

@app.route("/queue")
def show_queue():
    return {"queue": queue}

@app.route("/waiting")
def waiting():
    return render_template("waiting.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if add_user(username, password):
            return "Compte créé ! <a href='/login'>Se connecter</a>"
        else:
            return "Nom d'utilisateur déjà pris."
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if check_user(username, password):
            session["username"] = username
            return redirect(f"/profile?username={username}")
        else:
            return "Identifiants incorrects."
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

@app.route("/add_friend", methods=["POST"])
def add_friend_route():
    if "username" not in session:
        return redirect("/login")
    friend = request.form["friend"]
    if add_friend(session["username"], friend):
        return redirect(f"/profile?username={session['username']}")
    else:
        return "Erreur lors de l'ajout de l'ami."

@app.route("/profile")
def profile():
    username = request.args.get("username")
    games = get_user_games(username)
    friends = get_friends(username)
    return render_template("profile.html", username=username, games=games, friends=friends)

@socketio.on('create_room')
def on_create(data):
    code = data['code']
    pseudo = data['pseudo']
    visible = data.get('visible', True)
    rooms[code] = {'players': [pseudo], 'visible': visible}
    join_room(code)
    emit('room_created', {'code': code})

@socketio.on('get_visible_rooms')
def get_visible_rooms():
    visibles = [{'code': code, 'players': room['players']} for code, room in rooms.items() if room['visible'] and len(room['players']) < 2]
    emit('visible_rooms', visibles)

@socketio.on('join_room')
def on_join(data):
    code = data['code']
    pseudo = data['pseudo']
    if code in rooms and len(rooms[code]['players']) < 2:
        rooms[code]['players'].append(pseudo)
        join_room(code)
        emit('room_joined', {'code': code}, room=code)
    else:
        emit('join_failed', {'reason': 'Salon plein ou inexistant'})

@socketio.on('game_message')
def on_game_message(data):
    code = data['code']
    emit('game_message', data, room=code)

@socketio.on('join_queue')
def on_join_queue(data):
    pseudo = data['pseudo']
    ip = request.remote_addr
    date = datetime.now().isoformat()
    sid = request.sid
    queue.append({'pseudo': pseudo, 'ip': ip, 'date': date, 'sid': sid})
    emit('queue_joined', {'pseudo': pseudo, 'date': date})

@socketio.on('leave_queue')
def on_leave_queue(data):
    sid = request.sid
    global queue
    queue = [p for p in queue if p['sid'] != sid]
    emit('queue_left')

@socketio.on('waiting_room')
def waiting_room(data):
    code = data['code']
    pseudo = data['pseudo']
    sid = request.sid
    if code not in waiting_rooms:
        waiting_rooms[code] = []
    if not any(p['pseudo'] == pseudo for p in waiting_rooms[code]):
        waiting_rooms[code].append({'pseudo': pseudo, 'ready': False, 'sid': sid})
    emit('waiting_status', {'players': waiting_rooms[code]}, room=code)
    join_room(code)

@socketio.on('waiting_chat')
def waiting_chat(data):
    code = data['code']
    pseudo = data['pseudo']
    msg = data['msg']
    emit('waiting_chat', {'pseudo': pseudo, 'msg': msg}, room=code)

@socketio.on('waiting_ready')
def waiting_ready(data):
    code = data['code']
    pseudo = data['pseudo']
    for p in waiting_rooms.get(code, []):
        if p['pseudo'] == pseudo:
            p['ready'] = True
    emit('waiting_status', {'players': waiting_rooms[code]}, room=code)
    # Si les deux sont prêts, on lance le jeu
    if len(waiting_rooms[code]) == 2 and all(p['ready'] for p in waiting_rooms[code]):
        emit('start_game', room=code)

# Exemple d'utilisation après la détection de la victoire :
# save_game(player1, player2, winner)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)