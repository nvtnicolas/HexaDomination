import sqlite3

def init_db():
    conn = sqlite3.connect('hexadom.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player1 TEXT,
        player2 TEXT,
        winner TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS friends (
        user_id INTEGER,
        friend_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(friend_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pseudo TEXT,
        ip TEXT,
        port INTEGER,
        date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player1 TEXT,
        player2 TEXT,
        board TEXT,
        finished INTEGER DEFAULT 0,
        winner INTEGER DEFAULT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS turns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        player INTEGER,
        move TEXT,
        FOREIGN KEY(match_id) REFERENCES matches(id)
    )''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('hexadom.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect('hexadom.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def get_user_games(username):
    conn = sqlite3.connect('hexadom.db')
    c = conn.cursor()
    c.execute("SELECT * FROM games WHERE player1=? OR player2=?", (username, username))
    games = c.fetchall()
    conn.close()
    return games

def add_to_queue(pseudo, ip, port):
    conn = sqlite3.connect('hexadom.db')
    c = conn.cursor()
    c.execute("INSERT INTO queue (pseudo, ip, port) VALUES (?, ?, ?)", (pseudo, ip, port))
    conn.commit()
    conn.close()

def get_queue():
    conn = sqlite3.connect('hexadom.db')
    c = conn.cursor()
    c.execute("SELECT * FROM queue ORDER BY date_joined")
    res = c.fetchall()
    conn.close()
    return res

def remove_from_queue(pseudo):
    conn = sqlite3.connect('hexadom.db')
    c = conn.cursor()
    c.execute("DELETE FROM queue WHERE pseudo = ?", (pseudo,))
    conn.commit()
    conn.close()

def add_friend(user, friend):
    conn = sqlite3.connect('hexadom.db')
    c = conn.cursor()
    # Récupère les IDs
    c.execute("SELECT id FROM users WHERE username=?", (user,))
    user_id = c.fetchone()
    c.execute("SELECT id FROM users WHERE username=?", (friend,))
    friend_id = c.fetchone()
    if user_id and friend_id:
        try:
            c.execute("INSERT INTO friends (user_id, friend_id) VALUES (?, ?)", (user_id[0], friend_id[0]))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    return False

def get_friends(username):
    conn = sqlite3.connect('hexadom.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    user_id = c.fetchone()
    if not user_id:
        return []
    c.execute("SELECT u.username FROM friends f JOIN users u ON f.friend_id = u.id WHERE f.user_id=?", (user_id[0],))
    friends = [row[0] for row in c.fetchall()]
    conn.close()
    return friends

def save_game(player1, player2, winner):
    conn = sqlite3.connect('hexadom.db')
    c = conn.cursor()
    c.execute("INSERT INTO games (player1, player2, winner) VALUES (?, ?, ?)", (player1, player2, winner))
    conn.commit()
    conn.close()

# Ajoute d'autres fonctions pour gérer les matchs et les tours...