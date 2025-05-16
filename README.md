# 🎮 HexaDomination

**HexaDomination** est un jeu de stratégie multijoueur en local, basé sur un système de tuiles hexagonales. Il fonctionne avec un serveur de matchmaking, des clients connectés via sockets, et une base de données pour le suivi des parties.

---

## 🚀 Fonctionnalités principales

- Serveur de matchmaking avec gestion de file d'attente
- Jeu de plateau au **tour par tour** entre deux joueurs
- Génération dynamique du plateau
- Clients connectés par **sockets TCP**
- Interface utilisateur en Pygame
- Suivi des parties dans une base SQLite (matchs, coups)
- Algorithme de validation de coups + détection de victoire

---

## 🧱 Architecture

+-----------+ Socket +-----------+ SQL +-------------+
| Client A | <----------------> | Serveur | <-------------> | BDD (SQLite) |
+-----------+ +-----------+ +-------------+
▲ ▲
| |
+-----------+ +-----------+
| Client B | <----------------> | Matchmaking + Logique |
+-----------+ +-----------+

## 🛠️ Technologies utilisées

| Élément         | Technologie      |
|----------------|------------------|
| Langage         | Python 3.x       |
| Interface       | Pygame (Client)  |
| Réseau          | Sockets (TCP/IP) |
| BDD             | SQLite           |
| Format messages | JSON             |

---

## 🗃️ Structure du projet

HexaDomination/
├── client/
│ ├── client.py
│ ├── ihm.py
│ └── utils.py
├── server/
│ ├── server.py
│ ├── matchmaking.py
│ ├── game_logic.py
│ └── database.py
├── assets/
│ └── (images, sons)
├── db/
│ └── hexa_domination.db
├── README.md
└── requirements.txt

---

## 📝 Base de données

### Tables principales :
- `file_attente(id, pseudo, ip, port, date_arrivee)`
- `matchs(id, joueur1_ip, joueur2_ip, plateau, etat, resultat)`
- `tours(id, match_id, joueur, coup, timestamp)`

---

## 🎮 Lancer le projet

### 1. Installer les dépendances :

pip install -r requirements.txt

### 2. Lancer le serveur :

cd server
python server.py

### 3. Lancer les clients (sur deux terminaux) :

cd client
python client.py
