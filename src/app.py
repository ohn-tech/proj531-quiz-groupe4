# Module pour lire les variables d'environnement
import os
# Module pour ouvrir le navigateur automatiquement
import webbrowser
# Module pour stocker les questions (géré via la base de données relationnelle)
import json
# Module pour générer des codes de partage aléatoires et sûrs
import secrets
# Module pour enregistrer la date de création d'un quiz
from datetime import datetime
# Importe les outils Flask nécessaires
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify
# Lecture des quiz importés depuis un fichier texte, et vérification avant enregistrement
from import_quiz import lire_fichier, verifier_quiz, TAILLE_FICHIER_MAX

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
        # Permet d'accéder aux colonnes par leur nom : ligne["login"]
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
            password TEXT
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
            login_creator TEXT NOT NULL
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
            id_quizz INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS folder (
            id_folder INTEGER PRIMARY KEY AUTOINCREMENT,
            name_folder TEXT NOT NULL,
            format TEXT,
            date_folder TEXT,
            id_quizz INTEGER NOT NULL
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
    # Liste des quiz : les quiz publics, plus les quiz privés de l'utilisateur connecté.
    # Les quiz privés des autres sont masqués (on y accède seulement avec leur code de partage).
    quizz_crees = db.execute(
        # nb_questions : nombre de questions du quiz, compté dans la table questions
        "SELECT id_quizz, title, description, timer, is_public, login_creator, code, category, difficulty, "
        "(SELECT COUNT(*) FROM questions WHERE questions.id_quizz = quizz.id_quizz) AS nb_questions "
        "FROM quizz WHERE is_public = 1 OR login_creator = ? ORDER BY id_quizz DESC",
        (utilisateur,),
    ).fetchall()

    liste_quiz = FAUX_QUIZ + [
        {
            "id": f"custom-{q['id_quizz']}",
            "titre": q["title"],
            "description": q["description"],
            "duree": q["timer"],
            "nb_questions": q["nb_questions"],
            "visibilite": q["is_public"],
            # Vrai si l'utilisateur connecté a créé ce quiz : lui seul voit le bouton « Supprimer »
            "est_createur": q["login_creator"] == utilisateur,
            # Sujet et difficulté : vides (None) pour les quiz importés depuis un fichier
            "sujet": q["category"],
            "difficulte": q["difficulty"],
            "createur": q["login_creator"],
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

# Règles des quiz (README) : 1 à 20 questions, 2 à 6 réponses, une seule bonne réponse
NB_QUESTIONS_MAX = 20
NB_REPONSES_MIN = 2
NB_REPONSES_MAX = 6
DIFFICULTES = {"Facile", "Moyen", "Difficile"}
# Code de partage des quiz privés : 6 caractères, sans les lettres et chiffres faciles à confondre (O/0, I/1, L)
ALPHABET_CODE = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
LONGUEUR_CODE = 6

# Génère un code de partage de 6 caractères, pas encore utilisé par un autre quiz
def generer_code_partage():
    while True:
        code = "".join(secrets.choice(ALPHABET_CODE) for _ in range(LONGUEUR_CODE))
        if get_db().execute("SELECT 1 FROM quizz WHERE code = ?", (code,)).fetchone() is None:
            return code

# Lit les questions envoyées par le formulaire de création. Noms des champs :
# questions[i][question], questions[i][award], questions[i][answers][j][answer]
# et questions[i][correct] (numéro de la bonne réponse).
# Renvoie (liste des questions, None) si tout est correct, sinon (None, message d'erreur).
def lire_questions_formulaire(form):
    questions = []
    i = 0
    while f"questions[{i}][question]" in form:
        numero = i + 1
        if numero > NB_QUESTIONS_MAX:
            return None, f"Un quiz contient au maximum {NB_QUESTIONS_MAX} questions."

        texte = form.get(f"questions[{i}][question]", "").strip()
        award = form.get(f"questions[{i}][award]", "1").strip()
        bonne = form.get(f"questions[{i}][correct]", "")
        reponses = []
        while f"questions[{i}][answers][{len(reponses)}][answer]" in form:
            reponses.append(form.get(f"questions[{i}][answers][{len(reponses)}][answer]", "").strip())

        if not texte:
            return None, f"La question {numero} n'a pas d'énoncé."
        if not award.isdecimal():
            return None, f"Les points de la question {numero} doivent être un nombre positif."
        if not NB_REPONSES_MIN <= len(reponses) <= NB_REPONSES_MAX:
            return None, f"La question {numero} doit avoir entre {NB_REPONSES_MIN} et {NB_REPONSES_MAX} réponses."
        if any(not reponse for reponse in reponses):
            return None, f"Une réponse de la question {numero} est vide."
        if not bonne.isdecimal() or int(bonne) >= len(reponses):
            return None, f"Choisissez la bonne réponse de la question {numero}."

        questions.append({
            "question": texte,
            "award": int(award),
            "reponses": reponses,
            "bonne": int(bonne),
        })
        i += 1

    if not questions:
        return None, "Ajoutez au moins une question."
    return questions, None

# Enregistre un quiz dans quizz, puis ses questions et leurs réponses (is_correct = 1 pour la bonne).
# questions : liste de {"question", "award", "reponses", "bonne"} (numéro de la bonne réponse).
# origin : "saisie" (formulaire de création) ou "import" (fichier texte).
# Renvoie le code de partage du quiz s'il est privé, sinon None.
def enregistrer_quizz(title, description, timer, is_public, category, difficulty, origin, questions):
    # Un quiz privé (is_public = 0) reçoit un code de partage
    code = generer_code_partage() if is_public == 0 else None
    db = get_db()

    # 1. Insertion du quiz
    id_quizz = db.execute(
        "INSERT INTO quizz (title, description, timer, is_public, code, origin, date_quizz, "
        "category, difficulty, login_creator) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (title, description, timer, is_public, code, origin,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S"), category, difficulty, session["utilisateur"]),
    ).lastrowid

    # 2. Insertion de chaque question, puis de ses réponses
    for question in questions:
        id_question = db.execute(
            "INSERT INTO questions (question, award, id_quizz) VALUES (?, ?, ?)",
            (question["question"], question["award"], id_quizz),
        ).lastrowid
        for index, texte_reponse in enumerate(question["reponses"]):
            db.execute(
                "INSERT INTO answers (text_answer, is_correct, id_question) VALUES (?, ?, ?)",
                (texte_reponse, 1 if index == question["bonne"] else 0, id_question),
            )

    db.commit()
    return code

# Route de création d'un quiz : enregistre le quiz dans quizz, puis ses questions et leurs réponses
@app.route("/quiz/creer", methods=["POST"])
def creer_quizz():
    if "utilisateur" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    category = request.form.get("subject", "").strip()
    difficulty = request.form.get("difficulty", "")
    timer = request.form.get("timer", "").strip()
    is_public = request.form.get("is_public", "1")

    # Vérifie les informations du quiz ; en cas d'erreur, message et retour à l'accueil
    erreur = None
    if not title or len(title) > 100:
        erreur = "Le titre est obligatoire et ne doit pas dépasser 100 caractères."
    elif len(description) > 300:
        erreur = "La description ne doit pas dépasser 300 caractères."
    elif not category or len(category) > 100:
        erreur = "Le sujet est obligatoire et ne doit pas dépasser 100 caractères."
    elif difficulty not in DIFFICULTES:
        erreur = "Choisissez une difficulté."
    elif not timer.isdecimal() or not 10 <= int(timer) <= 3600:
        erreur = "La durée doit être comprise entre 10 et 3600 secondes."
    elif is_public not in {"0", "1"}:
        erreur = "Choisissez une visibilité valide pour le quiz."
    questions = None
    if erreur is None:
        questions, erreur = lire_questions_formulaire(request.form)
    if erreur is not None:
        flash(erreur, "erreur")
        return redirect(url_for("accueil"))

    code = enregistrer_quizz(title, description, int(timer), int(is_public), category, difficulty,
                             "saisie", questions)
    if code:
        flash(f"Votre quiz a été créé. Code de partage : {code}", "succes")
    else:
        flash("Votre quiz a été créé avec succès.", "succes")
    return redirect(url_for("accueil"))

# Taille maximale d'un document envoyé pour générer un quiz (5 Mo)
TAILLE_DOCUMENT_MAX = 5_000_000

# Génération factice en attendant le vrai générateur (côté backend) :
# renvoie des questions d'exemple pour pouvoir tester l'interface d'import.
# À remplacer par la vraie génération à partir du texte du document.
def generer_quiz_factice(nom_fichier, nb_questions):
    titre = os.path.splitext(nom_fichier)[0].strip()[:100] or "Quiz généré"
    questions = [
        {
            "texte": f"Question d'exemple n° {numero} (à remplacer par le vrai générateur)",
            "choix": ["Bonne réponse", "Mauvaise réponse A", "Mauvaise réponse B", "Mauvaise réponse C"],
            "reponse": 0,
        }
        for numero in range(1, nb_questions + 1)
    ]
    return {"titre": titre, "questions": questions}

# Route de la page d'import (générer un quiz à partir d'un document, ou importer un quiz écrit)
@app.route("/quiz/importer")
def importer_quiz():
    if "utilisateur" not in session:
        return redirect(url_for("login"))
    return render_template("importer.html")

# Analyse le fichier envoyé par la page d'import et renvoie le quiz en JSON, sans l'enregistrer
@app.route("/quiz/importer/analyser", methods=["POST"])
def analyser_import():
    if "utilisateur" not in session:
        return jsonify(erreurs=["Votre session a expiré. Reconnectez-vous puis recommencez."]), 401

    fichier = request.files.get("fichier")
    mode = request.form.get("mode")
    if fichier is None or not fichier.filename:
        return jsonify(erreurs=["Choisissez un fichier à importer."]), 400
    extension = os.path.splitext(fichier.filename)[1].lower()

    # Mode « quiz déjà écrit » : fichier texte au format QUIZ: / Q: / + / -
    if mode == "quiz":
        if extension != ".txt":
            return jsonify(erreurs=["Un quiz déjà écrit doit être un fichier texte (.txt)."]), 400
        # Un octet de plus que la limite pour détecter un fichier trop gros
        quiz_lu, erreurs = lire_fichier(fichier.read(TAILLE_FICHIER_MAX + 1))
        if erreurs:
            return jsonify(erreurs=erreurs), 400
        return jsonify(titre=quiz_lu["titre"], questions=quiz_lu["questions"], simule=False)

    # Mode « document » : un cours en TXT ou PDF, à partir duquel on génère les questions
    if mode == "document":
        if extension not in {".txt", ".pdf"}:
            return jsonify(erreurs=["Le document doit être un fichier TXT ou PDF."]), 400
        nb_questions = request.form.get("nb_questions", "")
        if not nb_questions.isdecimal() or not 1 <= int(nb_questions) <= NB_QUESTIONS_MAX:
            return jsonify(erreurs=[f"Choisissez entre 1 et {NB_QUESTIONS_MAX} questions."]), 400

        contenu = fichier.read(TAILLE_DOCUMENT_MAX + 1)
        if not contenu:
            return jsonify(erreurs=["Le fichier est vide."]), 400
        if len(contenu) > TAILLE_DOCUMENT_MAX:
            return jsonify(erreurs=["Le document est trop volumineux (5 Mo maximum)."]), 400
        # Vérifie que le fichier est bien ce que son extension annonce
        if extension == ".pdf" and not contenu.startswith(b"%PDF"):
            return jsonify(erreurs=["Ce fichier n'est pas un PDF valide."]), 400
        if extension == ".txt":
            try:
                contenu.decode("utf-8-sig")
            except UnicodeDecodeError:
                return jsonify(erreurs=["Le fichier texte doit être encodé en UTF-8."]), 400

        quiz_genere = generer_quiz_factice(fichier.filename, int(nb_questions))
        return jsonify(titre=quiz_genere["titre"], questions=quiz_genere["questions"], simule=True)

    return jsonify(erreurs=["Choisissez ce que vous voulez faire du fichier."]), 400

# Enregistre le quiz relu et corrigé dans la page d'import (données envoyées en JSON)
# dans les tables quizz, questions et answers, avec origin = "import"
@app.route("/quiz/importer/enregistrer", methods=["POST"])
def enregistrer_import():
    if "utilisateur" not in session:
        return jsonify(erreurs=["Votre session a expiré. Reconnectez-vous puis recommencez."]), 401

    donnees = request.get_json(silent=True)
    if not isinstance(donnees, dict):
        return jsonify(erreurs=["Données invalides."]), 400

    titre = donnees.get("titre")
    visibilite = donnees.get("visibilite")
    duree = donnees.get("duree")
    questions, erreurs = verifier_quiz(titre, donnees.get("questions"))
    if visibilite not in {"public", "prive"}:
        erreurs.append("Choisissez une visibilité valide pour le quiz.")
    if isinstance(duree, bool) or not isinstance(duree, int) or not 10 <= duree <= 3600:
        erreurs.append("Le minuteur doit être compris entre 10 et 3600 secondes.")
    if erreurs:
        return jsonify(erreurs=erreurs), 400

    # Convertit les questions au format de enregistrer_quizz (1 point par question)
    questions_base = [
        {"question": q["texte"], "award": 1, "reponses": q["choix"], "bonne": q["reponse"]}
        for q in questions
    ]
    titre = titre.strip()
    # Pas de sujet ni de difficulté dans le format d'import : colonnes laissées vides (NULL)
    code = enregistrer_quizz(titre, "Importé depuis un fichier.", duree, 1 if visibilite == "public" else 0,
                             None, None, "import", questions_base)

    nb = len(questions_base)
    message = f"Le quiz « {titre} » a été enregistré ({nb} question{'s' if nb > 1 else ''})."
    if code:
        message += f" Code de partage : {code}"
    flash(message, "succes")
    return jsonify(redirection=url_for("accueil"))

@app.route("/rejoindre", methods=["GET", "POST"])
def rejoindre_quiz():
    if request.method == "POST":
        # Le champ du formulaire s'appelle "code_partage" (rejoindre.html)
        code = request.form.get("code_partage", "").strip().upper()
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
        for i, question in enumerate(quizz["questions"]):
            if request.form.get(f"q{i}") == str(question["reponse"]):
                score += 1
        message = f"{quizz['titre']} : {score} / {len(quizz['questions'])} bonnes réponses."
        if request.form.get("temps_ecoule") == "1":
            message = "Temps écoulé ! " + message
        
        if "utilisateur" not in session:
            return render_template("quiz.html", quiz=quizz, resultat=message)
        flash(message, "succes")
        return redirect(url_for("accueil"))

    return render_template("quiz.html", quiz=quizz)

@app.route("/historique")
def historique():
    if "utilisateur" not in session:
        return redirect(url_for("login"))
    return render_template("bientot.html", titre="Historique")

# Supprime un quiz : seul son créateur en a le droit (« le créateur est l'administrateur de son quiz »)
@app.route("/quiz/<quiz_id>/supprimer", methods=["POST"])
def supprimer_quizz(quiz_id):
    # Il faut être connecté pour supprimer un quiz
    if "utilisateur" not in session:
        return redirect(url_for("login"))

    # Seuls les quiz de la base ont un créateur : leur identifiant est de la forme « custom-5 ».
    # Les quiz factices (FAUX_QUIZ, identifiants « 1 », « 2 »...) ne peuvent pas être supprimés.
    if not str(quiz_id).startswith("custom-"):
        abort(404)
    # Garde seulement le numéro après « custom- »
    identifiant = str(quiz_id)[7:]
    if not identifiant.isdecimal():
        abort(404)

    db = get_db()
    # Récupère le créateur du quiz demandé
    ligne = db.execute(
        "SELECT login_creator FROM quizz WHERE id_quizz = ?", (int(identifiant),)
    ).fetchone()
    # Quiz introuvable : erreur 404
    if ligne is None:
        abort(404)

    # Vérification des droits : si l'utilisateur connecté n'est pas le créateur, on refuse
    # (protège aussi contre quelqu'un qui enverrait la requête à la main, sans passer par le bouton)
    if ligne["login_creator"] != session["utilisateur"]:
        flash("Seul le créateur de ce quiz peut le supprimer.")
        return redirect(url_for("accueil"))

    id_quizz = int(identifiant)
    # Supprime d'abord ce qui dépend du quiz, pour ne laisser aucune ligne orpheline :
    # les réponses de ses questions, ses questions, les tentatives et le document source
    db.execute(
        "DELETE FROM answers WHERE id_question IN (SELECT id_question FROM questions WHERE id_quizz = ?)",
        (id_quizz,),
    )
    db.execute("DELETE FROM questions WHERE id_quizz = ?", (id_quizz,))
    db.execute("DELETE FROM attempts WHERE id_quizz = ?", (id_quizz,))
    db.execute("DELETE FROM folder WHERE id_quizz = ?", (id_quizz,))
    # Puis le quiz lui-même
    db.execute("DELETE FROM quizz WHERE id_quizz = ?", (id_quizz,))
    # Enregistre les suppressions dans la base
    db.commit()

    flash("Le quiz a été supprimé.", "succes")
    return redirect(url_for("accueil"))

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
