# 🏰 HexaDomination - Tower Defense

**HexaDomination** devient un **jeu de Tower Defense compétitif** : deux joueurs s'affrontent en parallèle, chacun sur son propre plateau, et le but est de survivre le plus longtemps possible face à des vagues d'ennemis. Le gagnant est celui qui tient le plus de tours !

---

## 🚀 Fonctionnalités principales

- Serveur de matchmaking avec gestion de file d'attente
- Deux joueurs connectés en simultané, chacun sur son plateau
- Génération dynamique des vagues d'ennemis
- Clients connectés par **sockets TCP**
- Interface utilisateur en Pygame
- Suivi des parties dans une base SQLite (matchs, scores, vagues)
- Algorithme de gestion des vagues, tours et score
- Détection automatique du vainqueur (celui qui survit le plus longtemps)

---

## 🧱 Architecture

+-----------+ Socket +-----------+ SQL +-------------+
| Client A | <----------------> | Serveur | <-------------> | BDD (SQLite) |
+-----------+ +-----------+ +-------------+
▲                                         ▲
|                                         |
+-----------+                   +-----------+
| Client B | <----------------> | Matchmaking + Logique |
+-----------+                   +-----------+

---

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
│   ├── client.py
│   ├── ihm.py
│   └── utils.py
├── server/
│   ├── server.py
│   ├── matchmaking.py
│   ├── game_logic.py
│   └── database.py
├── assets/
│   └── (images, sons)
├── db/
│   └── hexa_domination.db
├── README.md
└── requirements.txt

---

## 📝 Base de données

### Tables principales :
- `file_attente(id, pseudo, ip, port, date_arrivee)`
- `matchs(id, joueur1_ip, joueur2_ip, score1, score2, etat, resultat)`
- `vagues(id, match_id, joueur, numero_vague, ennemis, timestamp)`

---

## 🎮 Lancer le projet

### 1. Installer les dépendances :

```bash
pip install -r requirements.txt
```

### 2. Lancer le serveur :

```bash
cd server
python server.py
```

### 3. Lancer les clients (sur deux terminaux) :

```bash
cd client
python client.py
```
