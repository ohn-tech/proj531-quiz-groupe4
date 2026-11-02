# Tests de l'import de quiz depuis un fichier texte
# Lancement depuis la racine du dépôt : python -m unittest discover tests
import os
import sys
import unittest

# Permet d'importer les modules du dossier src/
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))

from import_quiz import lire_fichier, lire_quiz, verifier_quiz


# Lit un fichier d'exemple du dossier data/
def lire_exemple(nom):
    with open(os.path.join(RACINE, "data", nom), "rb") as fichier:
        return lire_fichier(fichier.read())


# Critères d'acceptation de la carte : les deux fichiers d'exemple fournis par Omar
class TestFichiersExemples(unittest.TestCase):
    # exemple_quiz.txt doit être importé sans erreur
    def test_exemple_valide(self):
        quiz, erreurs = lire_exemple("exemple_quiz.txt")
        self.assertEqual(erreurs, [])
        self.assertEqual(quiz["titre"], "Capitales d'Europe")
        self.assertEqual(len(quiz["questions"]), 3)
        premiere = quiz["questions"][0]
        self.assertEqual(premiere["texte"], "Quelle est la capitale de l'Espagne ?")
        self.assertEqual(premiere["choix"], ["Barcelone", "Madrid", "Séville"])
        # "reponse" est l'indice de la bonne réponse dans "choix"
        self.assertEqual(premiere["choix"][premiere["reponse"]], "Madrid")

    # exemple_quiz_erreur.txt doit être refusé, avec une erreur par problème
    def test_exemple_erreur(self):
        quiz, erreurs = lire_exemple("exemple_quiz_erreur.txt")
        self.assertIsNone(quiz)
        self.assertEqual(len(erreurs), 3)
        # Question sans bonne réponse
        self.assertIn("Ligne 3", erreurs[0])
        self.assertIn("pas de bonne réponse", erreurs[0])
        # Question avec une seule réponse
        self.assertIn("Ligne 7", erreurs[1])
        self.assertIn("au moins 2 réponses", erreurs[1])
        # Ligne qui ne commence ni par Q:, ni par +, ni par -
        self.assertIn("Ligne 10", erreurs[2])
        self.assertIn("ligne non reconnue", erreurs[2])


# Chaque erreur possible dans un fichier doit être refusée avec un message clair
class TestErreurs(unittest.TestCase):
    # Vérifie que le texte est refusé avec un message contenant "attendu"
    def verifier_refus(self, texte, attendu):
        quiz, erreurs = lire_quiz(texte)
        self.assertIsNone(quiz)
        self.assertTrue(any(attendu in erreur for erreur in erreurs), erreurs)

    # Fichier qui ne contient que des lignes vides
    def test_fichier_vide(self):
        self.verifier_refus("\n\n", "vide")

    # Première ligne sans « QUIZ: »
    def test_sans_titre(self):
        self.verifier_refus("Q: Question ?\n+ A\n- B", "commencer par « QUIZ: »")

    # « QUIZ: » présent mais sans titre derrière
    def test_titre_vide(self):
        self.verifier_refus("QUIZ:\n\nQ: Question ?\n+ A\n- B", "titre du quiz est vide")

    # Un titre mais aucune ligne « Q: »
    def test_sans_question(self):
        self.verifier_refus("QUIZ: Titre", "aucune question")

    # Des réponses sans ligne « Q: » au-dessus
    def test_reponse_hors_question(self):
        self.verifier_refus("QUIZ: Titre\n\n+ A\n- B", "n'appartient à aucune question")

    # Deux lignes « + » dans la même question (une seule bonne réponse autorisée)
    def test_plusieurs_bonnes_reponses(self):
        self.verifier_refus("QUIZ: Titre\n\nQ: Question ?\n+ A\n+ B", "plusieurs bonnes réponses")

    # 7 réponses pour une question (6 maximum)
    def test_trop_de_reponses(self):
        reponses = "\n".join(["+ A"] + [f"- {i}" for i in range(6)])
        self.verifier_refus(f"QUIZ: Titre\n\nQ: Question ?\n{reponses}", "plus de 6 réponses")

    # Fichier enregistré en latin-1 au lieu d'UTF-8
    def test_encodage_invalide(self):
        quiz, erreurs = lire_fichier("QUIZ: Été".encode("latin-1"))
        self.assertIsNone(quiz)
        self.assertIn("UTF-8", erreurs[0])

    # Fichier de plus de 100 Ko
    def test_fichier_trop_gros(self):
        quiz, erreurs = lire_fichier(b"x" * 100_001)
        self.assertIsNone(quiz)
        self.assertIn("trop volumineux", erreurs[0])


# Le format doit rester souple sur la mise en forme
class TestFormat(unittest.TestCase):
    # Espaces en trop, lignes vides multiples et fins de ligne Windows sont acceptés
    def test_format_souple(self):
        texte = "\r\n  QUIZ:  Titre  \r\n\r\n\r\nQ:Question ?\r\n  -  A\r\n+B\r\n"
        quiz, erreurs = lire_quiz(texte)
        self.assertEqual(erreurs, [])
        self.assertEqual(quiz["titre"], "Titre")
        self.assertEqual(quiz["questions"], [{"texte": "Question ?", "choix": ["A", "B"], "reponse": 1}])


# Vérification du quiz relu et modifié dans la page d'import, juste avant l'enregistrement
class TestVerificationAvantEnregistrement(unittest.TestCase):
    # Question correcte servant de base aux tests ; on modifie un seul champ à la fois
    def question(self, **modifications):
        question = {"texte": "Question ?", "choix": ["A", "B"], "reponse": 0}
        question.update(modifications)
        return question

    # Un quiz correct est accepté, et les espaces autour des textes sont retirés
    def test_quiz_valide_nettoye(self):
        questions, erreurs = verifier_quiz("Titre", [self.question(texte="  Q ?  ", choix=[" A ", "B"])])
        self.assertEqual(erreurs, [])
        self.assertEqual(questions, [{"texte": "Q ?", "choix": ["A", "B"], "reponse": 0}])

    # Un titre fait uniquement d'espaces est refusé
    def test_titre_vide(self):
        _, erreurs = verifier_quiz("   ", [self.question()])
        self.assertIn("Le titre du quiz est obligatoire.", erreurs)

    # Un quiz sans aucune question est refusé
    def test_aucune_question(self):
        _, erreurs = verifier_quiz("Titre", [])
        self.assertTrue(any("entre 1 et 20 questions" in erreur for erreur in erreurs))

    # Chaque problème donne un message qui indique le numéro de la question
    def test_question_incomplete(self):
        questions, erreurs = verifier_quiz("Titre", [
            self.question(),                    # 1 : correcte
            self.question(texte=""),            # 2 : énoncé vide
            self.question(choix=["A"]),         # 3 : une seule réponse
            self.question(choix=["A", " "]),    # 4 : réponse vide
            self.question(reponse=None),        # 5 : aucune bonne réponse cochée
            self.question(reponse=5),           # 6 : indice hors de la liste
            self.question(reponse=True),        # 7 : un booléen n'est pas un indice
        ])
        # Au moins une erreur : rien n'est enregistré
        self.assertEqual(questions, [])
        self.assertEqual(erreurs, [
            "Question 2 : l'énoncé est vide.",
            "Question 3 : il faut entre 2 et 6 réponses.",
            "Question 4 : une réponse est vide.",
            "Question 5 : choisissez la bonne réponse.",
            "Question 6 : choisissez la bonne réponse.",
            "Question 7 : choisissez la bonne réponse.",
        ])


# Permet aussi de lancer ce fichier directement : python tests/test_import_quiz.py
if __name__ == "__main__":
    unittest.main()
