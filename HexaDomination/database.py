import sqlite3

def init_db():
    conn = sqlite3.connect('hexadom.db')
    c = conn.cursor()
    # File d'attente
    c.execute('''CREATE TABLE IF NOT EXISTS queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pseudo TEXT,
        ip TEXT,
        port INTEGER,
        date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # Matchs
    c.execute('''CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player1 TEXT,
        player2 TEXT,
        board TEXT,
        finished INTEGER DEFAULT 0,
        winner INTEGER DEFAULT NULL
    )''')
    # Tours
    c.execute('''CREATE TABLE IF NOT EXISTS turns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        player INTEGER,
        move TEXT,
        FOREIGN KEY(match_id) REFERENCES matches(id)
    )''')
    conn.commit()
    conn.close()

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

# Ajoute d'autres fonctions pour gérer les matchs et les tours...