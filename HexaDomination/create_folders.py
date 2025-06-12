import os

# Créer les dossiers nécessaires
folders = [
    'static',
    'static/css',
    'static/js',
    'static/img',
    'static/img/avatars',
    'templates'
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Dossier créé: {folder}")

print("Tous les dossiers ont été créés!")