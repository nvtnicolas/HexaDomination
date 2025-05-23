# HexaDomination Web

**HexaDomination Web** est une version web multijoueur de HexaDomination, jouable directement depuis un navigateur. Deux joueurs peuvent créer ou rejoindre un salon grâce à un code, puis jouer ensemble en temps réel.

---

## Fonctionnalités

- Création et rejoint de salons privés via un code.
- Communication en temps réel grâce à Flask-SocketIO.
- Interface web simple (HTML/JS) accessible depuis n'importe quel navigateur sur le réseau.

---

## Installation

1. **Cloner le dépôt ou copier les fichiers nécessaires**  
   Placez-vous dans le dossier du projet.

2. **Installer les dépendances Python**  
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer le serveur web**  
   ```bash
   python webserver.py
   ```

4. **Accéder au jeu**  
   Depuis un navigateur, allez à l’adresse suivante :  
   ```
   http://<IP_DU_SERVEUR>:5000
   ```
   Remplacez `<IP_DU_SERVEUR>` par l’adresse IP de la machine qui héberge le serveur.

---

## Structure du projet

```
HexaDomination/
│
├── webserver.py           # Serveur Flask + SocketIO
├── requirements.txt       # Dépendances Python
└── templates/
    └── index.html         # Interface web du jeu
```

---

## Utilisation

- **Créer un salon** : Cliquez sur "Créer un salon", choisissez un code (ou laissez vide pour un code aléatoire), puis partagez ce code avec votre adversaire.
- **Rejoindre un salon** : Cliquez sur "Rejoindre un salon", entrez le code reçu, puis attendez que la partie commence.
- **Jouer** : L’interface de jeu reste à compléter en JavaScript pour gérer le plateau, les actions, etc.

---

## Développement

- Le cœur du jeu (plateau, règles, etc.) doit être implémenté en JavaScript dans `index.html`.
- Le serveur Python ne fait que relayer les messages et gérer les salons.

---

## Remarques

- Le jeu fonctionne en local ou sur un réseau local. Pour jouer à distance, ouvrez le port 5000 sur votre box/routeur.
- Pygame et Tkinter ne sont plus utilisés : tout se passe dans le navigateur.

---

## Auteurs

- Projet adapté pour le web par [Votre Nom]  
- Basé sur HexaDomination (projet original)

---