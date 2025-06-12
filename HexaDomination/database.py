import sqlite3
import hashlib
import os
from datetime import datetime

DATABASE = 'hexadomination.db'

def get_db_connection():
    """Créer une connexion à la base de données"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialiser la base de données avec les tables nécessaires"""
    conn = get_db_connection()
    
    # Table des utilisateurs
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            avatar_path TEXT DEFAULT NULL
        )
    ''')
    
    # Table des amis
    conn.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1 TEXT NOT NULL,
            user2 TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user1, user2)
        )
    ''')
    
    # Table des parties
    conn.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            player1 TEXT NOT NULL,
            player2 TEXT NOT NULL,
            winner TEXT DEFAULT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP DEFAULT NULL,
            game_data TEXT DEFAULT NULL
        )
    ''')
    
    # Table des statistiques
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            games_played INTEGER DEFAULT 0,
            games_won INTEGER DEFAULT 0,
            games_lost INTEGER DEFAULT 0,
            total_playtime INTEGER DEFAULT 0,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Base de données initialisée avec succès")

def hash_password(password):
    """Hasher un mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    """Ajouter un nouvel utilisateur"""
    try:
        conn = get_db_connection()
        password_hash = hash_password(password)
        
        conn.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            (username, password_hash)
        )
        
        # Initialiser les statistiques
        conn.execute(
            'INSERT INTO user_stats (username) VALUES (?)',
            (username,)
        )
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # L'utilisateur existe déjà
        return False
    except Exception as e:
        print(f"Erreur lors de la création de l'utilisateur: {e}")
        return False

def check_user(username, password):
    """Vérifier les identifiants d'un utilisateur"""
    conn = get_db_connection()
    
    if password:  # Si on vérifie le mot de passe
        password_hash = hash_password(password)
        user = conn.execute(
            'SELECT * FROM users WHERE username = ? AND password_hash = ?',
            (username, password_hash)
        ).fetchone()
    else:  # Si on vérifie juste l'existence
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?',
            (username,)
        ).fetchone()
    
    conn.close()
    return user

def add_friend(username, friend_username):
    """Ajouter un ami"""
    try:
        conn = get_db_connection()
        
        # Vérifier que l'ami existe
        friend_exists = conn.execute(
            'SELECT id FROM users WHERE username = ?',
            (friend_username,)
        ).fetchone()
        
        if not friend_exists:
            conn.close()
            return False
        
        # Ajouter la relation d'amitié (bidirectionnelle)
        conn.execute(
            'INSERT INTO friends (user1, user2) VALUES (?, ?)',
            (username, friend_username)
        )
        
        # Ajouter dans l'autre sens aussi
        try:
            conn.execute(
                'INSERT INTO friends (user1, user2) VALUES (?, ?)',
                (friend_username, username)
            )
        except sqlite3.IntegrityError:
            pass  # La relation inverse existe peut-être déjà
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # L'amitié existe déjà
        conn.close()
        return False
    except Exception as e:
        print(f"Erreur lors de l'ajout d'ami: {e}")
        conn.close()
        return False

def get_friends(username):
    """Récupérer la liste des amis d'un utilisateur"""
    conn = get_db_connection()
    
    friends = conn.execute(
        'SELECT user2 FROM friends WHERE user1 = ? ORDER BY created_at DESC',
        (username,)
    ).fetchall()
    
    conn.close()
    return [friend['user2'] for friend in friends]

def save_game(player1, player2, winner, game_id=None, game_data=None):
    """Sauvegarder une partie"""
    try:
        conn = get_db_connection()
        
        if not game_id:
            game_id = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{player1}_{player2}"
        
        conn.execute(
            '''INSERT INTO games (game_id, player1, player2, winner, ended_at, game_data) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (game_id, player1, player2, winner, datetime.now(), game_data)
        )
        
        # Mettre à jour les statistiques
        # Joueur 1
        conn.execute(
            '''UPDATE user_stats 
               SET games_played = games_played + 1,
                   games_won = games_won + ?,
                   games_lost = games_lost + ?
               WHERE username = ?''',
            (1 if winner == player1 else 0, 1 if winner != player1 else 0, player1)
        )
        
        # Joueur 2
        conn.execute(
            '''UPDATE user_stats 
               SET games_played = games_played + 1,
                   games_won = games_won + ?,
                   games_lost = games_lost + ?
               WHERE username = ?''',
            (1 if winner == player2 else 0, 1 if winner != player2 else 0, player2)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la partie: {e}")
        return False

def get_user_games(username, limit=10):
    """Récupérer l'historique des parties d'un utilisateur"""
    conn = get_db_connection()
    
    games = conn.execute(
        '''SELECT game_id, player1, player2, winner, ended_at 
           FROM games 
           WHERE player1 = ? OR player2 = ? 
           ORDER BY ended_at DESC 
           LIMIT ?''',
        (username, username, limit)
    ).fetchall()
    
    conn.close()
    return [tuple(game) for game in games]

def get_user_stats(username):
    """Récupérer les statistiques d'un utilisateur"""
    conn = get_db_connection()
    
    stats = conn.execute(
        'SELECT * FROM user_stats WHERE username = ?',
        (username,)
    ).fetchone()
    
    conn.close()
    return stats

def get_leaderboard(limit=10):
    """Récupérer le classement des meilleurs joueurs"""
    conn = get_db_connection()
    
    leaderboard = conn.execute(
        '''SELECT username, games_played, games_won, games_lost,
                  ROUND(CAST(games_won AS FLOAT) / CAST(games_played AS FLOAT) * 100, 2) as win_rate
           FROM user_stats 
           WHERE games_played > 0
           ORDER BY games_won DESC, win_rate DESC 
           LIMIT ?''',
        (limit,)
    ).fetchall()
    
    conn.close()
    return leaderboard

def delete_user(username):
    """Supprimer un utilisateur (pour les tests)"""
    try:
        conn = get_db_connection()
        
        # Supprimer des amis
        conn.execute('DELETE FROM friends WHERE user1 = ? OR user2 = ?', (username, username))
        
        # Supprimer des parties
        conn.execute('DELETE FROM games WHERE player1 = ? OR player2 = ?', (username, username))
        
        # Supprimer les stats
        conn.execute('DELETE FROM user_stats WHERE username = ?', (username,))
        
        # Supprimer l'utilisateur
        conn.execute('DELETE FROM users WHERE username = ?', (username,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur lors de la suppression de l'utilisateur: {e}")
        return False

# Fonction pour créer un utilisateur de test
def create_test_users():
    """Créer des utilisateurs de test"""
    test_users = [
        ("alice", "password123"),
        ("bob", "password123"),
        ("charlie", "password123")
    ]
    
    for username, password in test_users:
        if add_user(username, password):
            print(f"Utilisateur de test créé: {username}")
        else:
            print(f"L'utilisateur {username} existe déjà")

if __name__ == "__main__":
    # Initialiser la base de données
    init_db()
    
    # Créer des utilisateurs de test (optionnel)
    create_test_users()
    
    print("Configuration de la base de données terminée")