# Lecture d'un quiz depuis un fichier texte (format décrit dans le README) :
#
#   QUIZ: Titre du quiz
#
#   Q: Énoncé de la question
#   + Bonne réponse
#   - Mauvaise réponse
#
# Une ligne vide sépare deux questions.

# Limites (les mêmes que pour le formulaire de création)
TAILLE_TITRE_MAX = 100
NB_QUESTIONS_MAX = 20
NB_REPONSES_MIN = 2
NB_REPONSES_MAX = 6
# Taille maximale du fichier, en octets (100 Ko)
TAILLE_FICHIER_MAX = 100_000


# Raccourcit une ligne trop longue pour l'afficher dans un message d'erreur
def extrait(texte, longueur=40):
    return texte if len(texte) <= longueur else texte[:longueur] + "…"


# Lit le contenu d'un fichier envoyé (en octets) et renvoie (quiz, erreurs)
def lire_fichier(octets):
    if len(octets) > TAILLE_FICHIER_MAX:
        return None, [f"Le fichier est trop volumineux ({TAILLE_FICHIER_MAX // 1000} Ko maximum)."]
    try:
        # "utf-8-sig" accepte aussi les fichiers enregistrés avec un BOM (Bloc-notes)
        texte = octets.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None, ["Le fichier doit être un fichier texte encodé en UTF-8."]
    return lire_quiz(texte)


# Analyse le texte d'un quiz et renvoie (quiz, erreurs)
# - quiz : {"titre": ..., "questions": [{"texte", "choix", "reponse"}]}, ou None en cas d'erreur
# - erreurs : liste de messages, triés par numéro de ligne
def lire_quiz(texte):
    # Chaque erreur est un couple (numéro de ligne, message) pour pouvoir les trier
    erreurs = []
    titre = None
    questions = []
    # Question en cours de lecture (None après une ligne vide)
    question = None
    premiere_ligne = True

    for numero, ligne in enumerate(texte.splitlines(), start=1):
        ligne = ligne.strip()

        # Ligne vide : fin de la question en cours
        if not ligne:
            question = None
            continue

        # La première ligne non vide doit donner le titre
        if premiere_ligne:
            premiere_ligne = False
            if ligne.startswith("QUIZ:"):
                titre = ligne[5:].strip()
                if not titre:
                    erreurs.append((numero, "le titre du quiz est vide (écrivez-le après « QUIZ: »)."))
                elif len(titre) > TAILLE_TITRE_MAX:
                    erreurs.append((numero, f"le titre ne doit pas dépasser {TAILLE_TITRE_MAX} caractères."))
                continue
            erreurs.append((numero, "le fichier doit commencer par « QUIZ: » suivi du titre du quiz."))
            # On continue quand même pour signaler les autres erreurs

        if ligne.startswith("QUIZ:"):
            erreurs.append((numero, "« QUIZ: » ne peut apparaître qu'une fois, sur la première ligne."))

        # Nouvelle question
        elif ligne.startswith("Q:"):
            question = {"texte": ligne[2:].strip(), "choix": [], "bonnes": [], "ligne": numero}
            questions.append(question)
            if not question["texte"]:
                erreurs.append((numero, "l'énoncé de la question est vide (écrivez-le après « Q: »)."))

        # Réponse : « + » pour une bonne réponse, « - » pour une mauvaise
        elif ligne[0] in "+-":
            reponse = ligne[1:].strip()
            if question is None:
                erreurs.append((numero, f"la réponse « {extrait(reponse)} » n'appartient à aucune question "
                                        "(il manque une ligne « Q: » juste au-dessus)."))
            elif not reponse:
                erreurs.append((numero, f"la réponse est vide (écrivez-la après « {ligne[0]} »)."))
            else:
                if ligne[0] == "+":
                    question["bonnes"].append(len(question["choix"]))
                question["choix"].append(reponse)

        # Tout le reste est refusé
        else:
            erreurs.append((numero, f"ligne non reconnue « {extrait(ligne)} ». Une ligne doit commencer "
                                    "par « Q: » (question), « + » (bonne réponse) ou « - » (mauvaise réponse)."))

    # Fichier vide ou sans aucune question
    if premiere_ligne:
        return None, ["Le fichier est vide."]
    if not questions:
        erreurs.append((0, "Le fichier ne contient aucune question (une question commence par « Q: »)."))
    elif len(questions) > NB_QUESTIONS_MAX:
        erreurs.append((0, f"Le quiz contient {len(questions)} questions, le maximum est {NB_QUESTIONS_MAX}."))

    # Vérifications sur chaque question une fois toutes ses réponses lues
    for question in questions:
        nb_reponses = len(question["choix"])
        if nb_reponses < NB_REPONSES_MIN:
            erreurs.append((question["ligne"], f"la question doit avoir au moins {NB_REPONSES_MIN} réponses "
                                               f"(elle en a {nb_reponses})."))
        elif nb_reponses > NB_REPONSES_MAX:
            erreurs.append((question["ligne"], f"la question ne doit pas avoir plus de {NB_REPONSES_MAX} réponses "
                                               f"(elle en a {nb_reponses})."))
        if nb_reponses and not question["bonnes"]:
            erreurs.append((question["ligne"], "la question n'a pas de bonne réponse (ligne commençant par « + »)."))
        elif len(question["bonnes"]) > 1:
            # La page de passage du quiz ne gère qu'une seule bonne réponse pour l'instant
            erreurs.append((question["ligne"], "la question a plusieurs bonnes réponses, une seule est autorisée."))

    if erreurs:
        # Trie par ligne ; les erreurs générales (ligne 0) sont affichées sans numéro
        erreurs.sort(key=lambda erreur: erreur[0])
        return None, [f"Ligne {numero} : {message}" if numero else message for numero, message in erreurs]

    quiz = {
        "titre": titre,
        "questions": [
            {"texte": question["texte"], "choix": question["choix"], "reponse": question["bonnes"][0]}
            for question in questions
        ],
    }
    return quiz, []


# Vérifie un quiz relu et modifié dans l'interface, juste avant de l'enregistrer
# Renvoie (questions nettoyées, erreurs)
def verifier_quiz(titre, questions):
    erreurs = []
    if not isinstance(titre, str) or not titre.strip():
        erreurs.append("Le titre du quiz est obligatoire.")
    elif len(titre.strip()) > TAILLE_TITRE_MAX:
        erreurs.append(f"Le titre ne doit pas dépasser {TAILLE_TITRE_MAX} caractères.")

    if not isinstance(questions, list) or not 1 <= len(questions) <= NB_QUESTIONS_MAX:
        erreurs.append(f"Le quiz doit contenir entre 1 et {NB_QUESTIONS_MAX} questions.")
        return [], erreurs

    propres = []
    for numero, question in enumerate(questions, start=1):
        if not isinstance(question, dict):
            erreurs.append(f"Question {numero} : format invalide.")
            continue
        texte = question.get("texte")
        choix = question.get("choix")
        reponse = question.get("reponse")

        if not isinstance(texte, str) or not texte.strip():
            erreurs.append(f"Question {numero} : l'énoncé est vide.")
        if not isinstance(choix, list) or not NB_REPONSES_MIN <= len(choix) <= NB_REPONSES_MAX:
            erreurs.append(f"Question {numero} : il faut entre {NB_REPONSES_MIN} et {NB_REPONSES_MAX} réponses.")
        elif any(not isinstance(option, str) or not option.strip() for option in choix):
            erreurs.append(f"Question {numero} : une réponse est vide.")
        # bool est un sous-type de int en Python : on l'exclut explicitement
        elif isinstance(reponse, bool) or not isinstance(reponse, int) or not 0 <= reponse < len(choix):
            erreurs.append(f"Question {numero} : choisissez la bonne réponse.")
        else:
            propres.append({
                "texte": texte.strip(),
                "choix": [option.strip() for option in choix],
                "reponse": reponse,
            })

    return (propres if not erreurs else []), erreurs
