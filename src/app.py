# Module pour lire les variables d'environnement
import os
# Module pour ouvrir le navigateur automatiquement
import webbrowser
# Module pour stocker les questions des quiz sous forme de texte JSON
import json
# Module pour générer des codes de partage aléatoires et sûrs
import secrets
# Importe les outils Flask nécessaires
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort, jsonify
# Lecture des quiz importés depuis un fichier texte, et vérification avant enregistrement
from import_quiz import lire_fichier, verifier_quiz, TAILLE_FICHIER_MAX, NB_QUESTIONS_MAX

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

# Crée les tables si besoin et ajoute les colonnes manquantes des anciennes versions
# Renvoie True si la table "utilisateurs" vient d'être créée
def create_table():
    db = get_db()
    # Mémorise si la table existait déjà avant la création
    table_exists = db.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'utilisateurs'"
    ).fetchone() is not None
    db.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            login TEXT PRIMARY KEY,
            password TEXT,
            score INTEGER,
            role TEXT
        )
    """)
    # Ajoute la colonne "role" si la base a été créée avant son ajout
    colonnes_utilisateurs = {
        colonne["name"] for colonne in db.execute("PRAGMA table_info(utilisateurs)").fetchall()
    }
    if "role" not in colonnes_utilisateurs:
        db.execute("ALTER TABLE utilisateurs ADD COLUMN role TEXT")
    # Table des quiz créés depuis le site (questions stockées en JSON)
    db.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            description TEXT NOT NULL,
            duree INTEGER NOT NULL,
            questions TEXT NOT NULL,
            visibilite TEXT NOT NULL DEFAULT 'public',
            createur TEXT,
            code_partage TEXT
        )
    """)
    # Tables du futur modèle de données (quizz, questions, answers), utilisées par le formulaire de création
    db.executescript("""
        CREATE TABLE IF NOT EXISTS quizz (
            id_quizz INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            subject TEXT NOT NULL,
            is_public INTEGER NOT NULL DEFAULT 0,
            difficulty TEXT NOT NULL,
            code TEXT,
            link TEXT NOT NULL,
            timer INTEGER NOT NULL DEFAULT 120
        );
        CREATE TABLE IF NOT EXISTS questions (
            id_question INTEGER PRIMARY KEY AUTOINCREMENT,
            id_quizz INTEGER NOT NULL,
            question TEXT NOT NULL,
            award INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS answers (
            id_answer INTEGER PRIMARY KEY AUTOINCREMENT,
            id_question INTEGER NOT NULL,
            answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL DEFAULT 0
        );
    """)
    # Ajoute les colonnes manquantes de la table "quizzes"
    colonnes_quiz = {
        colonne["name"] for colonne in db.execute("PRAGMA table_info(quizzes)").fetchall()
    }
    if "visibilite" not in colonnes_quiz:
        db.execute("ALTER TABLE quizzes ADD COLUMN visibilite TEXT NOT NULL DEFAULT 'public'")
    if "createur" not in colonnes_quiz:
        db.execute("ALTER TABLE quizzes ADD COLUMN createur TEXT")
    if "code_partage" not in colonnes_quiz:
        db.execute("ALTER TABLE quizzes ADD COLUMN code_partage TEXT")
    # Deux quiz privés ne peuvent pas avoir le même code de partage
    db.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_quizzes_code_partage "
        "ON quizzes (code_partage) WHERE code_partage IS NOT NULL"
    )
    db.commit()
    return not table_exists

# Execute to add 2 ppl to the database before doing tests
# Does NOT need to be run every time we lunch the app.
def add_utilisateurs(tab = [("maram", "1234"), ("admin", "admin")]):
    db = get_db()
    for (login, mdp) in tab:
        # Correction : on vérifie avec fetchone() si l'utilisateur existe déjà
        if db.execute("SELECT 1 FROM utilisateurs WHERE login = ?", (login,)).fetchone() is None:
            db.execute("INSERT INTO utilisateurs (login, password, score) VALUES (?, ?, ?)", (login, mdp, 0))
    db.commit()

# Exécute une requête SQL et renvoie toutes les lignes du résultat
def request_database(query, params=()):
    db = get_db()
    # Sécurisation contre les injections SQL via des paramètres
    return db.execute(query, params).fetchall()

# Renvoie True si l'identifiant existe et que le mot de passe correspond
def verifier_identifiants(login, mdp):
    db = get_db()
    # Correction locale : fetchone() renvoie une ligne (ou None), pas directement le mot de passe
    ligne = db.execute("SELECT password FROM utilisateurs WHERE login = ?", (login,)).fetchone()
    return ligne is not None and ligne["password"] == mdp

# Crée un compte ; renvoie False si l'identifiant est déjà pris
def creer_utilisateur(login, mdp):
    db = get_db()
    # Vérifie si l'utilisateur existe déjà
    if db.execute("SELECT * FROM utilisateurs WHERE login = ?", (login,)).fetchone() is None:
        # Insertion sécurisée
        db.execute("INSERT INTO utilisateurs (login, password, score) VALUES (?, ?, ?)", (login, mdp, 0))
        db.commit()
        return True
    return False
# Supprime un compte ; renvoie True si une ligne a bien été supprimée
def delete_utilisateur(login):
    db = get_db()
    curseur = db.execute("DELETE FROM utilisateurs WHERE login = ?", (login,))
    db.commit()
    return curseur.rowcount > 0
# Correction locale : crée la table et les comptes de test au démarrage
# (sinon la table "utilisateurs" n'existe pas et la connexion échoue)
with app.app_context():
    if create_table():
        add_utilisateurs()


# Quiz factices en attendant le back-end
# "duree" = temps limite en secondes, "reponse" = indice du bon choix
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
    {
        "id": 3,
        "titre": "Géographie",
        "description": "Capitales, pays et continents.",
        "duree": 15,
        "questions": [
            {"texte": "Quelle est la capitale de la Tunisie ?", "choix": ["Sfax", "Tunis", "Sousse"], "reponse": 1},
        ],
    },
]


# Renvoie le quiz correspondant à l'identifiant, ou None s'il n'existe pas
def trouver_quiz(quiz_id):
    # Cherche d'abord parmi les quiz factices
    for quiz in FAUX_QUIZ:
        if str(quiz["id"]) == str(quiz_id):
            return quiz

    # Les quiz créés par les utilisateurs ont un identifiant de la forme "custom-<id>"
    if str(quiz_id).startswith("custom-"):
        # Retire le préfixe "custom-" pour garder l'id de la base
        identifiant = str(quiz_id)[7:]
        if identifiant.isdecimal():
            ligne = get_db().execute(
                "SELECT id, titre, description, duree, questions, visibilite, createur, code_partage "
                "FROM quizzes WHERE id = ?",
                (int(identifiant),),
            ).fetchone()
            # Convertit la ligne de la base au même format que les quiz factices
            if ligne is not None:
                return {
                    "id": f"custom-{ligne['id']}",
                    "titre": ligne["titre"],
                    "description": ligne["description"],
                    "duree": ligne["duree"],
                    "questions": json.loads(ligne["questions"]),
                    "visibilite": ligne["visibilite"],
                    "createur": ligne["createur"],
                    "code_partage": ligne["code_partage"],
                }
    return None


# Caractères possibles pour un code de partage (sans 0, O, 1, I ni L, faciles à confondre)
ALPHABET_CODE = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
LONGUEUR_CODE = 6


# Génère un code de partage aléatoire de 6 caractères, pas encore utilisé par un autre quiz
def generer_code_partage():
    while True:
        code = "".join(secrets.choice(ALPHABET_CODE) for _ in range(LONGUEUR_CODE))
        if get_db().execute("SELECT 1 FROM quizzes WHERE code_partage = ?", (code,)).fetchone() is None:
            return code


# Enregistre un quiz (créé sur le site ou importé) ; un quiz privé reçoit un code de partage
def enregistrer_quiz(titre, description, duree, questions, visibilite, createur):
    code_partage = generer_code_partage() if visibilite == "prive" else None
    # Les questions sont converties en texte JSON
    get_db().execute(
        "INSERT INTO quizzes (titre, description, duree, questions, visibilite, createur, code_partage) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (titre, description, duree, json.dumps(questions, ensure_ascii=False), visibilite, createur, code_partage),
    )
    get_db().commit()


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
    # Utilisateur connecté, ou None pour un visiteur
    utilisateur = session.get("utilisateur")
    # Quiz publics + quiz privés créés par l'utilisateur, du plus récent au plus ancien
    quiz_crees = get_db().execute(
        "SELECT id, titre, description, duree, questions, visibilite, createur, code_partage "
        "FROM quizzes WHERE visibilite = 'public' OR createur = ? ORDER BY id DESC",
        (utilisateur,),
    ).fetchall()
    # Ajoute les quiz de la base aux quiz factices, au même format
    liste_quiz = FAUX_QUIZ + [
        {
            "id": f"custom-{quiz['id']}",
            "titre": quiz["titre"],
            "description": quiz["description"],
            "duree": quiz["duree"],
            "questions": json.loads(quiz["questions"]),
            "visibilite": quiz["visibilite"],
            # Le code et le lien de partage ne sont montrés qu'au créateur du quiz
            "code_partage": quiz["code_partage"] if quiz["createur"] == utilisateur else None,
            "lien_partage": url_for(
                "quiz",
                quiz_id=f"custom-{quiz['id']}",
                code=quiz["code_partage"],
                _external=True,
            ) if quiz["visibilite"] == "prive" and quiz["createur"] == utilisateur else None,
        }
        for quiz in quiz_crees
    ]
    return render_template("accueil.html", utilisateur=utilisateur, liste_quiz=liste_quiz)


# Route de création d'un quiz (envoi du formulaire)
@app.route("/quiz/creer", methods=["POST"])
def creer_quiz():
    # Réservé aux utilisateurs connectés
    if "utilisateur" not in session:
        return redirect(url_for("login"))

    # Récupère les champs du formulaire (une liste par colonne pour les questions)
    titre = request.form.get("titre", "").strip()
    description = request.form.get("description", "").strip()
    duree = request.form.get("duree", "").strip()
    visibilite = request.form.get("visibilite", "public")
    textes = request.form.getlist("question_text[]")
    choix_a = request.form.getlist("choix_a[]")
    choix_b = request.form.getlist("choix_b[]")
    choix_c = request.form.getlist("choix_c[]")
    bonnes_reponses = request.form.getlist("bonne_reponse[]")

    # Vérifie chaque champ ; en cas d'erreur, message et retour à l'accueil
    if not titre or len(titre) > 100:
        flash("Le titre est obligatoire et ne doit pas dépasser 100 caractères.", "erreur")
        return redirect(url_for("accueil"))
    if len(description) > 300:
        flash("La description ne doit pas dépasser 300 caractères.", "erreur")
        return redirect(url_for("accueil"))
    if not duree.isdecimal() or not 10 <= int(duree) <= 3600:
        flash("La durée doit être comprise entre 10 et 3600 secondes.", "erreur")
        return redirect(url_for("accueil"))
    if visibilite not in {"public", "prive"}:
        flash("Choisissez une visibilité valide pour le quiz.", "erreur")
        return redirect(url_for("accueil"))
    # Entre 1 et 20 questions, et toutes les listes doivent avoir la même taille
    if not 1 <= len(textes) <= 20 or not (
        len(textes) == len(choix_a) == len(choix_b) == len(choix_c) == len(bonnes_reponses)
    ):
        flash("Ajoutez entre 1 et 20 questions complètes.", "erreur")
        return redirect(url_for("accueil"))

    # Regroupe les champs de chaque question dans un dictionnaire
    questions = []
    for texte, option_a, option_b, option_c, bonne_reponse in zip(
        textes, choix_a, choix_b, choix_c, bonnes_reponses
    ):
        texte = texte.strip()
        choix = [option_a.strip(), option_b.strip(), option_c.strip()]
        if not texte or any(not option for option in choix) or bonne_reponse not in {"0", "1", "2"}:
            flash("Chaque question doit avoir un énoncé, trois choix et une bonne réponse.", "erreur")
            return redirect(url_for("accueil"))
        questions.append({
            "texte": texte,
            "choix": choix,
            "reponse": int(bonne_reponse),
        })

    enregistrer_quiz(titre, description, int(duree), questions, visibilite, session["utilisateur"])
    flash("Votre quiz a été créé.", "succes")
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
    # Réservé aux utilisateurs connectés
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

    enregistrer_quiz(
        titre.strip(),
        "Importé depuis un fichier.",
        duree,
        questions,
        visibilite,
        session["utilisateur"],
    )
    nb = len(questions)
    flash(f"Le quiz « {titre.strip()} » a été enregistré ({nb} question{'s' if nb > 1 else ''}).", "succes")
    return jsonify(redirection=url_for("accueil"))


# Route pour rejoindre un quiz privé avec son code de partage
@app.route("/rejoindre", methods=["GET", "POST"])
def rejoindre_quiz():
    # Si le formulaire a été envoyé
    if request.method == "POST":
        # Les codes sont en majuscules : on accepte aussi une saisie en minuscules
        code = request.form.get("code_partage", "").strip().upper()
        # Cherche le quiz privé qui correspond au code
        quiz_prive = get_db().execute(
            "SELECT id FROM quizzes WHERE visibilite = 'prive' AND code_partage = ?",
            (code,),
        ).fetchone()
        if quiz_prive is None:
            flash("Code de partage invalide.", "erreur")
            return render_template("rejoindre.html")
        # Code correct : ouvre le quiz en passant le code dans l'URL
        return redirect(url_for("quiz", quiz_id=f"custom-{quiz_prive['id']}", code=code))
    # Affiche le formulaire de saisie du code
    return render_template("rejoindre.html")


# Route d'un quiz (affichage des questions et envoi des réponses)
@app.route("/quiz/<quiz_id>", methods=["GET", "POST"])
def quiz(quiz_id):
    # Récupère le quiz demandé
    quiz = trouver_quiz(quiz_id)
    # Quiz introuvable : page 404
    if quiz is None:
        abort(404)

    # Quiz privé : accessible au créateur ou à quelqu'un qui a le bon code
    if quiz.get("visibilite") == "prive":
        autorise = session.get("utilisateur") == quiz["createur"]
        # Bon code dans l'URL : on le retient dans la session pour les prochaines visites
        if quiz["code_partage"] and request.args.get("code") == quiz["code_partage"]:
            autorise = True
            quizs_autorises = session.setdefault("quiz_prives_autorises", [])
            if quiz_id not in quizs_autorises:
                quizs_autorises.append(quiz_id)
        # Code déjà saisi auparavant dans cette session
        if quiz_id in session.get("quiz_prives_autorises", []):
            autorise = True
        # Sinon, on demande le code de partage
        if not autorise:
            return redirect(url_for("rejoindre_quiz"))
    # Autre visibilité non publique : connexion obligatoire
    elif quiz.get("visibilite", "public") != "public" and "utilisateur" not in session:
        return redirect(url_for("login"))

    # Si le formulaire a été envoyé (par l'utilisateur ou par le minuteur)
    if request.method == "POST":
        # Compte les bonnes réponses (une question sans réponse compte faux)
        score = 0
        for i, question in enumerate(quiz["questions"]):
            if request.form.get(f"q{i}") == str(question["reponse"]):
                score += 1
        message = f"{quiz['titre']} : {score} / {len(quiz['questions'])} bonnes réponses."
        # Le minuteur a envoyé le formulaire tout seul
        if request.form.get("temps_ecoule") == "1":
            message = "Temps écoulé ! " + message
        # Visiteur non connecté : le résultat s'affiche directement sur la page du quiz
        if "utilisateur" not in session:
            return render_template("quiz.html", quiz=quiz, resultat=message)
        flash(message, "succes")
        # Retour à l'accueil (à remplacer par la page de résultat)
        return redirect(url_for("accueil"))

    # Affiche les questions du quiz
    return render_template("quiz.html", quiz=quiz)


# Route de l'historique des scores (page à compléter)
@app.route("/historique")
def historique():
    if "utilisateur" not in session:
        return redirect(url_for("login"))
    return render_template("bientot.html", titre="Historique")


# Route de déconnexion
@app.route("/logout")
def logout():
    # Vide la session (déconnecte l'utilisateur)
    session.clear()
    # Redirige vers la page de connexion
    return redirect(url_for("login"))


# Route de suppression du compte de l'utilisateur connecté
@app.route("/supprimer-compte", methods=["POST"])
def supprimer_compte():
    login = session.get("utilisateur")
    # Personne n'est connecté : retour à la connexion
    if login is None:
        return redirect(url_for("login"))

    # Échec de la suppression (compte introuvable)
    if not delete_utilisateur(login):
        flash("Impossible de supprimer le compte.", "erreur")
        return redirect(url_for("accueil"))

    # Déconnecte l'utilisateur puis le renvoie vers la page de connexion
    session.clear()
    flash("Votre compte a été supprimé.", "succes")
    return redirect(url_for("login"))


# Exécuté seulement si on lance ce fichier directement
if __name__ == "__main__":
    # Évite d'ouvrir le navigateur deux fois quand le mode debug redémarre le serveur
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        # Ouvre la page de connexion dans le navigateur
        webbrowser.open("http://127.0.0.1:5000/login")
    # Lance le serveur en mode debug
    app.run(debug=True)
