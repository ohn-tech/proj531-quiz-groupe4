# Module pour lire les variables d'environnement
import os
# Module pour ouvrir le navigateur automatiquement
import webbrowser
# Importe les outils Flask nécessaires
from flask import Flask, render_template, request, redirect, url_for, session, flash

import sqlite3
# Database
con = sqlite3.connect("quizzapp.db")
cur = con.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS utilisateurs (
        login TEXT PRIMARY KEY,
        password TEXT,
        score INTEGER
    )
""")

# Crée l'application Flask
app = Flask(__name__)
# Clé secrète utilisée pour signer la session (à changer en production)
app.secret_key = "change-moi"

# Execute to add 2 ppl to the database before doing tests
# Does NOT need to be run every time we lunch the app.
def add_faux_utilisateurs(tab = [("maram", "1234"), ("admin", "admin")]):
    for (login, mdp) in tab:
        if cur.execute(f"SELECT {mdp} FROM utilisateurs WHERE login = {login}") != None:
            return
    cur.executemany("INSERT INTO utilisateurs (login, password) VALUES (?, ?)", tab)
    con.commit()
    return

# Use for testing
def request_database(request):
    return cur.execute(request).fetchall()

# Vérifie si le couple identifiant / mot de passe est valide
def verifier_identifiants(login, mdp):
    # À remplacer par la fonction du back-end
    # Renvoie True si le mot de passe correspond à l'identifiant
    return cur.execute(f"SELECT password FROM utilisateurs WHERE login = {login}").fetchone() == mdp

# Crée un nouvel utilisateur, renvoie False s'il existe déjà
def creer_utilisateur(login, mdp):
    # À remplacer par la fonction du back-end
    # Si l'identifiant est libre
    if cur.execute(f"SELECT * FROM utilisateurs WHERE login = {login}").fetchone() == None:
        # Enregistre le nouvel utilisateur
        cur.execute(f"INSERT INTO utilisateurs (login, password) VALUES ({login}, {mdp})")
        con.commit()
        # Création réussie
        return True
    # Échec de la création
    return False


# Route de la page de connexion (affichage et envoi du formulaire)
@app.route("/login", methods=["GET", "POST"])
def login():
    # Si le formulaire a été envoyé
    if request.method == "POST":
        # Récupère l'identifiant saisi
        login = request.form["login"]
        # Récupère le mot de passe saisi
        mdp = request.form["mdp"]
        # Si les identifiants sont corrects
        if verifier_identifiants(login, mdp):
            # Mémorise l'utilisateur connecté dans la session
            session["utilisateur"] = login
            # Redirige vers la page d'accueil
            return redirect(url_for("accueil"))
        # Sinon, affiche un message d'erreur
        flash("Identifiant ou mot de passe incorrect.")
    # Affiche la page de connexion
    return render_template("login.html")


# Route de la page d'inscription (affichage et envoi du formulaire)
@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    # Si le formulaire a été envoyé
    if request.method == "POST":
        # Récupère l'identifiant sans les espaces autour
        login = request.form["login"].strip()
        # Récupère le mot de passe
        mdp = request.form["mdp"]
        # Récupère la confirmation du mot de passe
        confirmation = request.form["confirmation"]

        # Identifiant trop court
        if len(login) < 3:
            flash("L'identifiant doit contenir au moins 3 caractères.")
        # Mot de passe trop court
        elif len(mdp) < 4:
            flash("Le mot de passe doit contenir au moins 4 caractères.")
        # Les deux mots de passe sont différents
        elif mdp != confirmation:
            flash("Les mots de passe ne correspondent pas.")
        # L'identifiant existe déjà
        elif not creer_utilisateur(login, mdp):
            flash("Cet identifiant est déjà utilisé.")
        # Tout est valide
        else:
            # Connecte directement le nouvel utilisateur
            session["utilisateur"] = login
            # Redirige vers la page d'accueil
            return redirect(url_for("accueil"))

    # Affiche la page d'inscription (avec les éventuelles erreurs)
    return render_template("inscription.html")


# Route de la page d'accueil
@app.route("/")
def accueil():
    # Si personne n'est connecté
    if "utilisateur" not in session:
        # Redirige vers la page de connexion
        return redirect(url_for("login"))
    # Affiche l'accueil avec le nom de l'utilisateur connecté
    return render_template("accueil.html", utilisateur=session["utilisateur"])


# Route de déconnexion
@app.route("/logout")
def logout():
    # Vide la session (déconnecte l'utilisateur)
    session.clear()
    # Redirige vers la page de connexion
    return redirect(url_for("login"))


# Exécuté seulement si on lance ce fichier directement
if __name__ == "__main__":
    # Évite d'ouvrir le navigateur deux fois quand le mode debug redémarre le serveur
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        # Ouvre la page de connexion dans le navigateur
        webbrowser.open("http://127.0.0.1:5000/login")
    # Lance le serveur en mode debug
    app.run(debug=True)