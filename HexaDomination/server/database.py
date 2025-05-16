import sqlite3

class Database:
    def __init__(self, db_file):
        """Initialize the database connection."""
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        """Create the necessary tables in the database."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_attente (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pseudo TEXT NOT NULL,
                ip TEXT NOT NULL,
                port INTEGER NOT NULL,
                date_arrivee TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS matchs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                joueur1_ip TEXT NOT NULL,
                joueur2_ip TEXT NOT NULL,
                plateau TEXT NOT NULL,
                etat TEXT NOT NULL,
                resultat TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tours (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER NOT NULL,
                joueur TEXT NOT NULL,
                coup TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matchs (id)
            )
        ''')
        self.connection.commit()

    def insert_file_attente(self, pseudo, ip, port):
        """Insert a player into the waiting list."""
        self.cursor.execute('''
            INSERT INTO file_attente (pseudo, ip, port)
            VALUES (?, ?, ?)
        ''', (pseudo, ip, port))
        self.connection.commit()

    def insert_match(self, joueur1_ip, joueur2_ip, plateau, etat, resultat=None):
        """Insert a match record into the database."""
        self.cursor.execute('''
            INSERT INTO matchs (joueur1_ip, joueur2_ip, plateau, etat, resultat)
            VALUES (?, ?, ?, ?, ?)
        ''', (joueur1_ip, joueur2_ip, plateau, etat, resultat))
        self.connection.commit()

    def insert_tour(self, match_id, joueur, coup):
        """Insert a turn record into the database."""
        self.cursor.execute('''
            INSERT INTO tours (match_id, joueur, coup)
            VALUES (?, ?, ?)
        ''', (match_id, joueur, coup))
        self.connection.commit()

    def close(self):
        """Close the database connection."""
        self.connection.close()