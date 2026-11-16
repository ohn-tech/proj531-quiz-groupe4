# Génération d'un quiz à partir d'un document (TXT ou PDF) grâce à l'IA de Groq.
#
# Plan B : si l'IA ne peut pas être utilisée (pas d'internet, pas de clé, réponse invalide...),
# on renvoie la génération simulée, pour que la page d'import marche toujours (démo sans internet).
#
# Clé Groq : variable d'environnement GROQ_API_KEY, ou ligne GROQ_API_KEY=... dans le fichier .env
# à la racine du dépôt (ce fichier est ignoré par git : la clé n'est jamais poussée).
import io
import json
import os
import random

# Bibliothèque officielle de Groq (pip install -r requirements.txt) ; si elle manque, on passe au plan B
try:
    import groq
except ImportError:
    groq = None

from import_quiz import verifier_quiz, TAILLE_TITRE_MAX

# Modèle utilisé par défaut (modifiable avec GROQ_MODEL si Groq le retire)
MODELE_PAR_DEFAUT = "openai/gpt-oss-120b"
# Nombre maximal de caractères du document envoyés à l'IA (limite de la version gratuite de Groq)
TEXTE_MAX = 12_000
# Temps d'attente maximal de la réponse de Groq, en secondes
DELAI_MAX = 30
# Fichier .env à la racine du dépôt (un dossier au-dessus de src/)
FICHIER_ENV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")


# Erreur qui déclenche le plan B ; son message est affiché à l'utilisateur
class ErreurGeneration(Exception):
    pass


# Lit un réglage (GROQ_API_KEY, GROQ_MODEL) : d'abord dans les variables d'environnement, sinon dans .env
def lire_reglage(nom):
    valeur = os.environ.get(nom, "").strip()
    if valeur:
        return valeur
    try:
        with open(FICHIER_ENV, encoding="utf-8-sig") as fichier:
            for ligne in fichier:
                cle, _, contenu = ligne.partition("=")
                if cle.strip() == nom:
                    return contenu.strip().strip('"').strip("'")
    except OSError:
        pass
    return ""


# Renvoie le texte d'un document TXT ou PDF (contenu en octets)
def extraire_texte(contenu, extension):
    if extension == ".txt":
        return contenu.decode("utf-8-sig")
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ErreurGeneration("la lecture des PDF n'est pas installée (pip install -r requirements.txt)")
    try:
        lecteur = PdfReader(io.BytesIO(contenu))
        return "\n".join(page.extract_text() or "" for page in lecteur.pages)
    except Exception:
        raise ErreurGeneration("le PDF n'a pas pu être lu")


# Construit la consigne envoyée à l'IA
def consigne(texte, nb_questions):
    return (
        f"Tu es un professeur. À partir du document ci-dessous, écris un quiz de {nb_questions} questions "
        "à choix multiples, dans la langue du document.\n"
        "Règles :\n"
        "- chaque question porte sur une information présente dans le document ;\n"
        "- 4 réponses par question, une seule est correcte, les mauvaises réponses sont plausibles ;\n"
        "- questions et réponses courtes et sans ambiguïté ;\n"
        "- un titre court pour le quiz (moins de 60 caractères).\n"
        "Réponds uniquement avec un objet JSON de cette forme :\n"
        '{"titre": "...", "questions": [{"texte": "...", "choix": ["...", "...", "...", "..."], "reponse": 0}]}\n'
        "où « reponse » est l'indice (à partir de 0) de la bonne réponse dans « choix ».\n\n"
        f"Document :\n\"\"\"\n{texte}\n\"\"\""
    )


# Envoie la consigne à Groq et renvoie le texte de sa réponse
def appeler_groq(cle, modele, message):
    if groq is None:
        raise ErreurGeneration("la bibliothèque groq n'est pas installée (pip install -r requirements.txt)")
    # Une seule nouvelle tentative en cas d'échec, pour ne pas faire attendre l'utilisateur trop longtemps
    client = groq.Groq(api_key=cle, timeout=DELAI_MAX, max_retries=1)
    try:
        reponse = client.chat.completions.create(
            model=modele,
            messages=[{"role": "user", "content": message}],
            temperature=0.4,
            # Oblige Groq à répondre avec du JSON valide
            response_format={"type": "json_object"},
        )
    except groq.AuthenticationError:
        raise ErreurGeneration("la clé Groq est refusée")
    except groq.RateLimitError:
        raise ErreurGeneration("trop de demandes envoyées à Groq, réessayez dans une minute")
    except groq.APIConnectionError:
        raise ErreurGeneration("Groq est injoignable (pas de connexion internet ?)")
    except groq.NotFoundError:
        raise ErreurGeneration(f"le modèle « {modele} » n'existe plus chez Groq, choisissez-en un autre avec GROQ_MODEL")
    except groq.APIStatusError as erreur:
        raise ErreurGeneration(f"Groq a renvoyé une erreur (code {erreur.status_code})")
    except groq.GroqError:
        raise ErreurGeneration("Groq n'a pas pu générer le quiz")
    try:
        return reponse.choices[0].message.content
    except (AttributeError, IndexError):
        raise ErreurGeneration("la réponse de Groq est illisible")


# Transforme la réponse de l'IA en quiz vérifié : {"titre", "questions": [{"texte", "choix", "reponse"}]}
def lire_reponse_ia(texte_reponse, nb_questions, titre_defaut):
    try:
        quiz = json.loads(texte_reponse)
    except ValueError:
        raise ErreurGeneration("l'IA n'a pas renvoyé un quiz au bon format")
    if not isinstance(quiz, dict) or not isinstance(quiz.get("questions"), list):
        raise ErreurGeneration("l'IA n'a pas renvoyé un quiz au bon format")

    titre = quiz.get("titre")
    if not isinstance(titre, str) or not titre.strip():
        titre = titre_defaut
    titre = titre.strip()[:TAILLE_TITRE_MAX]

    # L'IA peut renvoyer plus de questions que demandé : on garde les premières
    questions, erreurs = verifier_quiz(titre, quiz["questions"][:nb_questions])
    if erreurs:
        raise ErreurGeneration("le quiz renvoyé par l'IA est incomplet")

    # L'IA met souvent la bonne réponse en premier : on mélange les réponses de chaque question
    for question in questions:
        bonne = question["choix"][question["reponse"]]
        random.shuffle(question["choix"])
        question["reponse"] = question["choix"].index(bonne)
    return {"titre": titre, "questions": questions}


# Plan B : questions d'exemple, sans internet
def generer_quiz_simule(titre, nb_questions):
    questions = [
        {
            "texte": f"Question d'exemple n° {numero} (génération simulée)",
            "choix": ["Bonne réponse", "Mauvaise réponse A", "Mauvaise réponse B", "Mauvaise réponse C"],
            "reponse": 0,
        }
        for numero in range(1, nb_questions + 1)
    ]
    return {"titre": titre, "questions": questions}


# Génère un quiz à partir d'un document. Renvoie (quiz, raison) :
# raison vaut None si l'IA a généré le quiz, sinon elle explique pourquoi on est passé au plan B.
def generer_quiz(contenu, extension, nom_fichier, nb_questions):
    titre_defaut = os.path.splitext(nom_fichier)[0].strip()[:TAILLE_TITRE_MAX] or "Quiz généré"
    try:
        cle = lire_reglage("GROQ_API_KEY")
        if not cle:
            raise ErreurGeneration("aucune clé Groq n'est configurée")
        texte = extraire_texte(contenu, extension).strip()
        if len(texte) < 50:
            raise ErreurGeneration("le document ne contient pas assez de texte lisible")
        modele = lire_reglage("GROQ_MODEL") or MODELE_PAR_DEFAUT
        reponse = appeler_groq(cle, modele, consigne(texte[:TEXTE_MAX], nb_questions))
        return lire_reponse_ia(reponse, nb_questions, titre_defaut), None
    except ErreurGeneration as erreur:
        return generer_quiz_simule(titre_defaut, nb_questions), str(erreur)
