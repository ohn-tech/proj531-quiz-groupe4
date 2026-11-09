# Module pour lire les variables d'environnement
import os
# Module pour ouvrir le navigateur automatiquement
import webbrowser
# Module pour stocker les questions (géré via la base de données relationnelle)
import json
# Module pour générer des codes de partage aléatoires et sûrs
import secrets
# Importe les outils Flask nécessaires
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
# Module pour récuppérer la date en format chaîne de charactère
from datetime import datetime

# Crée l'application Flask
app = Flask(__name__)
# Clé secrète utilisée pour signer la session (à changer en production)
app.secret_key = "change-moi"

# Module de base de données SQLite
import sqlite3
# Objet "g" de Flask : stocke des données le temps d'une requête
from flask import g

# Chemin du fichier de la base, à côté de app.py
DATABASE = os.path.join(app.root_path, "quizzapp.db")

# Renvoie la connexion à la base (ouverte une seule fois par requête)
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.row_factory = sqlite3.Row

    return g.db

# Ferme automatiquement la connexion à la fin de chaque requête
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Fonction à exécuter lors de la création de la base de données
def create_table():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS utilisateurs (
    login TEXT PRIMARY KEY,
    password TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS quizz (
    id_quizz INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    timer INTEGER NOT NULL DEFAULT 120,
    is_public INTEGER NOT NULL DEFAULT 0,
    code TEXT,
    origin TEXT,
    date_quizz TEXT,
    category TEXT,
    difficulty TEXT,
    login_creator TEXT NOT NULL,
    FOREIGN KEY (login_creator) REFERENCES utilisateurs(login)
    );

    CREATE TABLE IF NOT EXISTS questions (
    id_question INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    award INTEGER NOT NULL DEFAULT 0,
    id_quizz INTEGER NOT NULL,
    FOREIGN KEY (id_quizz) REFERENCES quizz(id_quizz)
    );

    CREATE TABLE IF NOT EXISTS answers (
    id_answer INTEGER PRIMARY KEY AUTOINCREMENT,
    text_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL DEFAULT 0,
    id_question INTEGER NOT NULL,
    FOREIGN KEY (id_question) REFERENCES questions(id_question)
    );

    CREATE TABLE IF NOT EXISTS attempts (
    id_attempt INTEGER PRIMARY KEY AUTOINCREMENT,
    score INTEGER NOT NULL DEFAULT 0,
    date_attempt TEXT NOT NULL,
    login TEXT NOT NULL,
    id_quizz INTEGER NOT NULL,
    FOREIGN KEY (login) REFERENCES utilisateurs(login)
    );

    CREATE TABLE IF NOT EXISTS folder (
    id_folder INTEGER PRIMARY KEY AUTOINCREMENT,
    name_folder TEXT NOT NULL,
    format TEXT,
    date_folder TEXT,
    id_quizz INTEGER NOT NULL,
    FOREIGN KEY (id_quizz) REFERENCES quizz(id_quizz)
    );
                     """)
    db.commit()

# Ajoute des utilisateurs de test si la table est vide
def add_utilisateurs(tab = [("maram", "1234"), ("admin", "admin")]):
    db = get_db()
    for (login, mdp) in tab:
        if db.execute("SELECT 1 FROM utilisateurs WHERE login = ?", (login,)).fetchone() is None:
            db.execute("INSERT INTO utilisateurs (login, password) VALUES (?, ?)", (login, mdp))
    db.commit()

# Initialisation de la base au démarrage
with app.app_context():
    create_table()
    add_utilisateurs()

# Quiz factices en mémoire (pour les tests rapides)
FAUX_QUIZ = [
    {
        "id": 1,
        "titre": "Culture générale",
        "description": "Testez vos connaissances sur des sujets variés.",
        "duree": 60,
        "questions": [
            {"texte": "Combien de continents y a-t-il ?", "choix": ["5", "6", "7"], "reponse": 2},
            {"texte": "Qui a peint la Joconde ?", "choix": ["Picasso", "Léonard de Vinci", "Van Gogh"], "reponse": 1},
            {"texte": "Quel est le plus grand océan ?", "choix": ["Atlantique", "Indien", "Pacifique"], "reponse": 2},
            {"texte": "Combien de jours dans une année bissextile ?", "choix": ["365", "366", "364"], "reponse": 1},
            {"texte": "Quelle planète est surnommée la planète rouge ?", "choix": ["Mars", "Vénus", "Jupiter"], "reponse": 0},
        ],
    },
    {
        "id": 2,
        "titre": "Python",
        "description": "Les bases du langage Python.",
        "duree": 45,
        "questions": [
            {"texte": "Quel mot-clé définit une fonction ?", "choix": ["func", "def", "function"], "reponse": 1},
            {"texte": "Que renvoie len([1, 2, 3]) ?", "choix": ["2", "3", "4"], "reponse": 1},
            {"texte": "Quel type est {} en Python ?", "choix": ["dict", "set", "list"], "reponse": 0},
        ],
    },
]

# Fonction centrale : Récupération d'un quiz et de ses questions/réponses associées par id_quizz
def trouver_quizz(id_quizz):
    # 1. Vérifie d'abord parmi les quiz factices
    for quizz in FAUX_QUIZ:
        if str(quizz["id"]) == str(id_quizz):
            return quizz

    # 2. Si c'est un quiz personnalisé de la base de données (ex: "custom-5" ou ID brut)
    identifiant = str(id_quizz)
    if identifiant.startswith("custom-"):
        identifiant = identifiant[7:]

    if identifiant.isdecimal():
        db = get_db()
        # Récupération des informations principales du quiz
        ligne_quizz = db.execute(
            "SELECT id_quizz, title, description, timer, is_public, login_creator, code "
            "FROM quizz WHERE id_quizz = ?",
            (int(identifiant),),
        ).fetchone()

        if ligne_quizz is not None:
            # Récupération des questions liées à cet id_quizz
            lignes_questions = db.execute(
                "SELECT id_question, question FROM questions WHERE id_quizz = ?",
                (ligne_quizz["id_quizz"],)
            ).fetchall()

            questions_formattees = []
            for q in lignes_questions:
                # Récupération des réponses (choix) associées à cette question
                lignes_reponses = db.execute(
                    "SELECT text_answer, is_correct FROM answers WHERE id_question = ?",
                    (q["id_question"],)
                ).fetchall()

                choix = [ans["text_answer"] for ans in lignes_reponses]
                # Trouve l'index de la bonne réponse
                reponse_idx = next((i for i, ans in enumerate(lignes_reponses) if ans["is_correct"] == 1), 0)

                questions_formattees.append({
                    "texte": q["question"],
                    "choix": choix,
                    "reponse": reponse_idx
                })

            return {
                "id": f"custom-{ligne_quizz['id_quizz']}",
                "titre": ligne_quizz["title"],
                "description": ligne_quizz["description"],
                "duree": ligne_quizz["timer"],
                "questions": questions_formattees,
                "visibilite": ligne_quizz["is_public"],
                "createur": ligne_quizz["login_creator"],
                "code": ligne_quizz["code"],
            }
    return None

# Authentification et gestion des utilisateurs
def verifier_identifiants(login, mdp):
    db = get_db()
    ligne = db.execute("SELECT password FROM utilisateurs WHERE login = ?", (login,)).fetchone()
    return ligne is not None and ligne["password"] == mdp

def creer_utilisateur(login, mdp):
    db = get_db()
    if db.execute("SELECT * FROM utilisateurs WHERE login = ?", (login,)).fetchone() is None:
        db.execute("INSERT INTO utilisateurs (login, password) VALUES (?, ?)", (login, mdp))
        db.commit()
        return True
    return False

def delete_utilisateur(login):
    db = get_db()
    curseur = db.execute("DELETE FROM utilisateurs WHERE login = ?", (login,))
    db.commit()
    return curseur.rowcount > 0

# --- ROUTES FLASK ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login = request.form["login"]
        mdp = request.form["mdp"]
        if verifier_identifiants(login, mdp):
            session["utilisateur"] = login
            return redirect(url_for("accueil"))
        flash("Identifiant ou mot de passe incorrect.")
    return render_template("login.html")

@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == "POST":
        login = request.form["login"].strip()
        mdp = request.form["mdp"]
        confirmation = request.form["confirmation"]

        if len(login) < 3:
            flash("L'identifiant doit contenir au moins 3 caractères.")
        elif len(mdp) < 4:
            flash("Le mot de passe doit contenir au moins 4 caractères.")
        elif mdp != confirmation:
            flash("Les mots de passe ne correspondent pas.")
        elif not creer_utilisateur(login, mdp):
            flash("Cet identifiant est déjà utilisé.")
        else:
            session["utilisateur"] = login
            return redirect(url_for("accueil"))
    return render_template("inscription.html")

@app.route("/")
def accueil():
    utilisateur = session.get("utilisateur")
    db = get_db()
    quizz_crees = db.execute(
        "SELECT id_quizz, title, description, timer, is_public, login_creator, code "
        "FROM quizz WHERE is_public = 1 OR login_creator = ? ORDER BY id_quizz DESC",
        (utilisateur,),
    ).fetchall()

    liste_quiz = FAUX_QUIZ + [
        {
            "id": f"custom-{q['id_quizz']}",
            "titre": q["title"],
            "description": q["description"],
            "duree": q["timer"],
            "visibilite": q["is_public"],
            "code_partage": q["code"] if q["login_creator"] == utilisateur else None,
            "lien_partage": url_for(
                "quizz_route",
                quiz_id=f"custom-{q['id_quizz']}",
                code=q["code"],
                _external=True,
            ) if q["is_public"] == 0 and q["login_creator"] == utilisateur else None,
        }
        for q in quizz_crees
    ]
    return render_template("accueil.html", utilisateur=utilisateur, liste_quiz=liste_quiz)

@app.route("/quiz/creer", methods=["POST"])
def creer_quizz():
    if "utilisateur" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    timer = request.form.get("timer", "").strip()
    is_public = int(request.form.get("is_public", 1))
    textes = request.form.getlist("question_text[]")
    choix_a = request.form.getlist("choix_a[]")
    choix_b = request.form.getlist("choix_b[]")
    choix_c = request.form.getlist("choix_c[]")
    bonnes_reponses = request.form.getlist("bonne_reponse[]")
    date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not title or len(title) > 100:
        flash("Le titre est obligatoire et ne doit pas dépasser 100 caractères.", "erreur")
        return redirect(url_for("accueil"))
    if not timer.isdecimal() or not 10 <= int(timer) <= 3600:
        flash("La durée doit être comprise entre 10 et 3600 secondes.", "erreur")
        return redirect(url_for("accueil"))

    code = secrets.token_urlsafe(9) if is_public == 0 else None
    db = get_db()
    
    # 1. Insertion du Quiz
    cursor = db.execute(
        "INSERT INTO quizz (title, description, timer, is_public, login_creator, code, date_quizz) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (title, description, int(timer), is_public, session["utilisateur"], code, date_actuelle)
    )
    id_quizz = cursor.lastrowid

    # 2. Insertion des Questions et de leurs Réponses respectives dans les tables relationnelles
    for texte, a, b, c, bonne in zip(textes, choix_a, choix_b, choix_c, bonnes_reponses):
        texte = texte.strip()
        if not texte:
            continue
        
        cursor_q = db.execute(
            "INSERT INTO questions (question, id_quizz) VALUES (?, ?)",
            (texte, id_quizz)
        )
        id_question = cursor_q.lastrowid

        choix_liste = [a.strip(), b.strip(), c.strip()]
        for index, choix_texte in enumerate(choix_liste):
            is_correct = 1 if str(index) == str(bonne) else 0
            db.execute(
                "INSERT INTO answers (text_answer, is_correct, id_question) VALUES (?, ?, ?)",
                (choix_texte, is_correct, id_question)
            )

    db.commit()
    flash("Votre quiz a été créé avec succès.", "succes")
    return redirect(url_for("accueil"))

@app.route("/rejoindre", methods=["GET", "POST"])
def rejoindre_quiz():
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        db = get_db()
        quiz_prive = db.execute(
            "SELECT id_quizz FROM quizz WHERE is_public = 0 AND code = ?",
            (code,),
        ).fetchone()
        if quiz_prive is None:
            flash("Code de partage invalide.", "erreur")
            return render_template("rejoindre.html")
        return redirect(url_for("quizz_route", quiz_id=f"custom-{quiz_prive['id_quizz']}", code=code))
    return render_template("rejoindre.html")

# Route d'un quiz (paramètre renommé quiz_id pour concorder avec l'URL)
@app.route("/quiz/<quiz_id>", methods=["GET", "POST"])
def quizz_route(quiz_id):
    quizz = trouver_quizz(quiz_id)
    if quizz is None:
        abort(404)

    # Gestion des quiz privés
    if quizz.get("visibilite") == 0:
        autorise = session.get("utilisateur") == quizz.get("createur")
        if quizz.get("code") and request.args.get("code") == quizz["code"]:
            autorise = True
            quizs_autorises = session.setdefault("quiz_prives_autorises", [])
            if quiz_id not in quizs_autorises:
                quizs_autorises.append(quiz_id)
        if quiz_id in session.get("quiz_prives_autorises", []):
            autorise = True
        if not autorise:
            return redirect(url_for("rejoindre_quiz"))

    if request.method == "POST":
        score = 0
        date_actuelle = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calcul du score
        for i, question in enumerate(quizz["questions"]):
            if request.form.get(f"q{i}") == str(question["reponse"]):
                score += 1

        # Enregistrement uniquement pour les utilisateurs connectés
        if "utilisateur" in session and str(quizz["id"]).startswith("custom-"):

            db = get_db()

            # Récupération de l'identifiant réel du quiz
            id_quizz = int(str(quizz["id"]).replace("custom-", ""))

            # Enregistrement de la tentative
            cursor = db.execute(
                """
                INSERT INTO attempts (score, date_attempt, login, id_quizz)
                VALUES (?, ?, ?, ?)
                """,
                (score, date_actuelle, session["utilisateur"], id_quizz)
            )

            db.commit()

        message = f"{quizz['titre']} : {score} / {len(quizz['questions'])} bonnes réponses."

        if request.form.get("temps_ecoule") == "1":
            message = "Temps écoulé ! " + message

        if "utilisateur" not in session:
            return render_template("quiz.html", quiz=quizz, resultat=message)

        flash(message, "succes")
        return redirect(url_for("accueil"))

    return render_template("quiz.html", quizz=quizz)

def historique_utilisateur(login):
    db = get_db()

    lignes = db.execute("""
        SELECT
            a.id_quizz,
            q.title AS titre,
            a.score,
            a.date_attempt AS date,
            (
                SELECT COUNT(*)
                FROM questions
                WHERE questions.id_quizz = a.id_quizz
            ) AS nb_questions
        FROM attempts AS a
        LEFT JOIN quizz AS q ON q.id_quizz = a.id_quizz
        WHERE a.login = ?
        ORDER BY a.date_attempt DESC
    """, (login,)).fetchall()

    return [
        {
            "id_quizz": int(ligne["id_quizz"]),
            "titre": ligne["titre"],
            "score": int(ligne["score"]),
            "nb_questions": int(ligne["nb_questions"]),
            "date": ligne["date"]
        }
        for ligne in lignes
    ]

@app.route("/historique")
def historique():
    if "utilisateur" not in session:
        return redirect(url_for("login"))

    historique = historique_utilisateur(session["utilisateur"])

    return render_template("historique.html", historique=historique)

@app.route("/admin")
def admin():
    if "utilisateur" not in session:
        return redirect(url_for("login"))
    if session["utilisateur"] != "admin":
        flash("Accès réservé à l'administrateur.")
        return redirect(url_for("accueil"))
    return render_template("bientot.html", titre="Administration")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/supprimer-compte", methods=["POST"])
def supprimer_compte():
    login = session.get("utilisateur")
    if login is None:
        return redirect(url_for("login"))
    if not delete_utilisateur(login):
        flash("Impossible de supprimer le compte.", "erreur")
        return redirect(url_for("accueil"))
    session.clear()
    flash("Votre compte a été supprimé.", "succes")
    return redirect(url_for("login"))

if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        webbrowser.open("http://127.0.0.1:5000/login")
    app.run(debug=True)