from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import hashlib
import os
from database import init_db, add_user, check_user, get_user_games, add_friend, get_friends, save_game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = 'static/img/avatars'
socketio = SocketIO(app, cors_allowed_origins="*")

# Créer le dossier d'avatars s'il n'existe pas
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

rooms = {}  # code_salon: {'players': [pseudo1, pseudo2], 'visible': True/False}
queue = []  # Liste des joueurs en attente : [{pseudo, ip, date, sid}]
waiting_rooms = {}  # code: [{'pseudo':..., 'ready':False, 'sid':...}, ...]
online_users = {}  # pseudo: {'sid': ..., 'in_game': False, 'game_id': None}

# Initialiser la base de données
init_db()

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
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Vérifications
        if not username or not password:
            return render_template("register.html", error="Tous les champs sont requis")
        
        if len(username) < 3:
            return render_template("register.html", error="Le nom d'utilisateur doit faire au moins 3 caractères")
        
        if len(password) < 6:
            return render_template("register.html", error="Le mot de passe doit faire au moins 6 caractères")
        
        if password != confirm_password:
            return render_template("register.html", error="Les mots de passe ne correspondent pas")
        
        # Vérifier si l'utilisateur existe déjà
        if check_user(username, password) is not None:
            return render_template("register.html", error="Ce nom d'utilisateur existe déjà")
        
        # Créer l'utilisateur
        if add_user(username, password):
            return render_template("register.html", success="Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
        else:
            return render_template("register.html", error="Erreur lors de la création du compte")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template("login.html", error="Nom d'utilisateur et mot de passe requis")
        
        user = check_user(username, password)
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('profile'))
        else:
            return render_template("login.html", error="Nom d'utilisateur ou mot de passe incorrect")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    username = session.get('username')
    if username and username in online_users:
        del online_users[username]
    
    session.clear()
    return redirect(url_for('index'))

@app.route("/add_friend", methods=["POST"])
def add_friend_route():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    friend = request.form.get('friend', '').strip()
    
    if not friend:
        flash('Nom d\'ami requis', 'error')
        return redirect(url_for('profile'))
    
    if friend == username:
        flash('Vous ne pouvez pas vous ajouter vous-même', 'error')
        return redirect(url_for('profile'))
    
    # Vérifier si l'ami existe
    if check_user(friend, '') is None:  # On ne vérifie que l'existence du nom
        flash('Cet utilisateur n\'existe pas', 'error')
        return redirect(url_for('profile'))
    
    if add_friend(username, friend):
        flash(f'{friend} ajouté à vos amis !', 'success')
    else:
        flash('Cet ami est déjà dans votre liste', 'error')
    
    return redirect(url_for('profile'))

@app.route("/profile")
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    # Marquer l'utilisateur comme en ligne
    online_users[username] = {
        'sid': None,
        'in_game': False,
        'game_id': None
    }
    
    # Récupérer les amis et l'historique
    friends = get_friends(username)
    games = get_user_games(username)
    
    # Statut des amis en ligne
    online_friends = {}
    for friend in friends:
        if friend in online_users:
            online_friends[friend] = online_users[friend]
    
    avatar_url = f"/static/img/avatars/{username}.jpg"
    if not os.path.exists(f"static/img/avatars/{username}.jpg"):
        avatar_url = "/static/img/default_avatar.png"
    
    return render_template("profile.html", 
                         username=username, 
                         friends=friends, 
                         games=games,
                         online_friends=online_friends,
                         avatar_url=avatar_url)

@app.route("/change_avatar", methods=["POST"])
def change_avatar():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    username = session['username']
    
    if 'avatar' not in request.files:
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('profile'))
    
    file = request.files['avatar']
    if file.filename == '':
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('profile'))
    
    if file and file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
        filename = f"{username}.jpg"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Avatar mis à jour !', 'success')
    else:
        flash('Format de fichier non supporté', 'error')
    
    return redirect(url_for('profile'))

@socketio.on('create_room')
def on_create(data):
    code = data.get('code', '').upper().strip()
    pseudo = data.get('pseudo', '').strip()
    visible = data.get('visible', True)
    
    if not code:
        code = ''.join([chr(65 + i) for i in [__import__('random').randint(0,25) for _ in range(6)]])
    
    if code in rooms:
        emit('create_failed', {'reason': 'Ce code existe déjà'})
        return
    
    rooms[code] = {'players': [pseudo], 'visible': visible}
    waiting_rooms[code] = [{'pseudo': pseudo, 'ready': False, 'sid': request.sid}]
    
    join_room(code)
    emit('room_created', {'code': code})

@socketio.on('get_visible_rooms')
def get_visible_rooms():
    visible = []
    for code, room in rooms.items():
        if room['visible'] and len(room['players']) < 2:
            visible.append({'code': code, 'players': room['players']})
    emit('visible_rooms', visible)

@socketio.on('join_room')
def on_join(data):
    code = data.get('code', '').upper().strip()
    pseudo = data.get('pseudo', '').strip()
    
    if code not in rooms:
        emit('join_failed', {'reason': 'Salon inexistant'})
        return
    
    if len(rooms[code]['players']) >= 2:
        emit('join_failed', {'reason': 'Salon complet'})
        return
    
    if pseudo in rooms[code]['players']:
        emit('join_failed', {'reason': 'Pseudo déjà utilisé dans ce salon'})
        return
    
    rooms[code]['players'].append(pseudo)
    waiting_rooms[code].append({'pseudo': pseudo, 'ready': False, 'sid': request.sid})
    
    join_room(code)
    emit('room_joined', {'code': code})
    
    # Notifier tous les joueurs de la room
    socketio.emit('waiting_status', {
        'players': waiting_rooms[code]
    }, room=code)

@socketio.on('game_message')
def on_game_message(data):
    code = data.get('code', '')
    msg = data.get('msg', '')
    if code:
        socketio.emit('game_message', {'msg': msg}, room=code)

@socketio.on('join_queue')
def on_join_queue(data):
    pseudo = data.get('pseudo', '').strip()
    if pseudo:
        queue_entry = {
            'pseudo': pseudo,
            'ip': request.environ.get('REMOTE_ADDR'),
            'date': datetime.now().strftime('%H:%M:%S'),
            'sid': request.sid
        }
        queue.append(queue_entry)
        emit('queue_joined', {'date': queue_entry['date']})

@socketio.on('leave_queue')
def on_leave_queue(data):
    global queue
    queue = [q for q in queue if q['sid'] != request.sid]

@socketio.on('waiting_room')
def waiting_room(data):
    code = data.get('code', '')
    pseudo = data.get('pseudo', '')
    
    if code in waiting_rooms:
        join_room(code)
        # Mettre à jour le SID
        for player in waiting_rooms[code]:
            if player['pseudo'] == pseudo:
                player['sid'] = request.sid
                break
        
        socketio.emit('waiting_status', {
            'players': waiting_rooms[code]
        }, room=code)

@socketio.on('waiting_chat')
def waiting_chat(data):
    code = data.get('code', '')
    pseudo = data.get('pseudo', '')
    msg = data.get('msg', '')
    
    if code and pseudo and msg:
        socketio.emit('waiting_chat', {
            'pseudo': pseudo,
            'msg': msg
        }, room=code)

@socketio.on('waiting_ready')
def waiting_ready(data):
    code = data.get('code', '')
    pseudo = data.get('pseudo', '')
    
    if code in waiting_rooms:
        for player in waiting_rooms[code]:
            if player['pseudo'] == pseudo:
                player['ready'] = True
                break
        
        # Vérifier si tous les joueurs sont prêts
        all_ready = len(waiting_rooms[code]) == 2 and all(p['ready'] for p in waiting_rooms[code])
        
        socketio.emit('waiting_status', {
            'players': waiting_rooms[code]
        }, room=code)
        
        if all_ready:
            # Lancer la partie
            socketio.emit('start_game', {}, room=code)
            
            # Marquer les joueurs comme en jeu
            for player in waiting_rooms[code]:
                username = player['pseudo']
                if username in online_users:
                    online_users[username]['in_game'] = True
                    online_users[username]['game_id'] = code

@socketio.on('disconnect')
def on_disconnect():
    # Retirer de la queue
    global queue
    queue = [q for q in queue if q['sid'] != request.sid]
    
    # Retirer des salles d'attente
    for code in list(waiting_rooms.keys()):
        waiting_rooms[code] = [p for p in waiting_rooms[code] if p['sid'] != request.sid]
        if not waiting_rooms[code]:
            del waiting_rooms[code]
            if code in rooms:
                del rooms[code]
        else:
            socketio.emit('waiting_status', {
                'players': waiting_rooms[code]
            }, room=code)

# Exemple d'utilisation après la détection de la victoire :
# save_game(player1, player2, winner)

if __name__ == "__main__":
    init_db()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)