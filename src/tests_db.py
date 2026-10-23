# Script de vérification : affiche le contenu de la table "utilisateurs"
# Importe l'application Flask et la fonction d'accès à la base
from app import app, request_database

# Un contexte d'application est nécessaire pour utiliser get_db() hors d'une requête
with app.app_context():
    # Récupère tous les identifiants et mots de passe enregistrés
    rows = request_database("SELECT login, password FROM utilisateurs")
    # En-tête du tableau affiché dans le terminal
    print("login | password")
    # Affiche une ligne par utilisateur
    for row in rows:
        print(f"{row['login']} | {row['password']}")