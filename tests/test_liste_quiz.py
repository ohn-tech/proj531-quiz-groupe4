# Tests de la liste des quiz (page d'accueil)
# Lancement depuis la racine du dépôt : python -m unittest discover tests
import os
import sys
import tempfile
import unittest

# Permet d'importer les modules du dossier src/
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))

import app as module_app


# Chaque test utilise sa propre base, vide, dans un dossier temporaire
class TestListeQuiz(unittest.TestCase):
    def setUp(self):
        self.dossier = tempfile.TemporaryDirectory()
        self.ancienne_base = module_app.DATABASE
        module_app.DATABASE = os.path.join(self.dossier.name, "test.db")
        module_app.app.config["TESTING"] = True
        self.client = module_app.app.test_client()

        with module_app.app.app_context():
            module_app.create_table()
            module_app.add_utilisateurs([("maram", "1234"), ("omar", "abcd")])
            # Quiz public de Maram : 3 questions
            self.ajouter_quiz("Capitales", 1, None, "maram", "Géographie", "Facile", 3)
            # Quiz privé de Maram : 2 questions, code de partage connu
            self.ajouter_quiz("Quiz secret", 0, "ABC234", "maram", "Histoire", "Difficile", 2)
            # Quiz public importé d'Omar : 1 question, sans sujet ni difficulté
            self.ajouter_quiz("Quiz importé", 1, None, "omar", None, None, 1)

    def tearDown(self):
        module_app.DATABASE = self.ancienne_base
        self.dossier.cleanup()

    # Ajoute un quiz et nb_questions questions (2 réponses chacune) directement dans la base
    def ajouter_quiz(self, titre, is_public, code, createur, sujet, difficulte, nb_questions):
        db = module_app.get_db()
        id_quizz = db.execute(
            "INSERT INTO quizz (title, description, timer, is_public, code, origin, category, "
            "difficulty, login_creator) VALUES (?, '', 60, ?, ?, 'saisie', ?, ?, ?)",
            (titre, is_public, code, sujet, difficulte, createur),
        ).lastrowid
        for numero in range(nb_questions):
            id_question = db.execute(
                "INSERT INTO questions (question, award, id_quizz) VALUES (?, 1, ?)",
                (f"Question {numero}", id_quizz),
            ).lastrowid
            db.execute("INSERT INTO answers (text_answer, is_correct, id_question) VALUES ('Oui', 1, ?)", (id_question,))
            db.execute("INSERT INTO answers (text_answer, is_correct, id_question) VALUES ('Non', 0, ?)", (id_question,))
        db.commit()

    # Renvoie le HTML de l'accueil vu par "login" (None = visiteur non connecté)
    def page_accueil(self, login=None):
        if login is not None:
            with self.client.session_transaction() as session:
                session["utilisateur"] = login
        reponse = self.client.get("/")
        self.assertEqual(reponse.status_code, 200)
        return reponse.get_data(as_text=True)

    # Le nombre de questions de chaque quiz est compté dans la table questions
    def test_nombre_de_questions(self):
        page = self.page_accueil("maram")
        self.assertIn("3 questions", page)
        self.assertIn("2 questions", page)
        # Singulier pour une seule question
        self.assertIn("1 question ·", page)

    # Un visiteur non connecté ne voit que les quiz publics
    def test_visiteur_ne_voit_pas_les_quiz_prives(self):
        page = self.page_accueil()
        self.assertIn("Capitales", page)
        self.assertNotIn("Quiz secret", page)
        self.assertNotIn("ABC234", page)

    # Un autre utilisateur ne voit pas le quiz privé de Maram, ni son code
    def test_quiz_prive_masque_pour_les_autres(self):
        page = self.page_accueil("omar")
        self.assertIn("Capitales", page)
        self.assertIn("Quiz importé", page)
        self.assertNotIn("Quiz secret", page)
        self.assertNotIn("ABC234", page)

    # Le créateur voit son quiz privé, avec son code de partage
    def test_createur_voit_son_quiz_prive(self):
        page = self.page_accueil("maram")
        self.assertIn("Quiz secret", page)
        self.assertIn("Quiz privé", page)
        self.assertIn("ABC234", page)

    # Le code de partage d'un quiz privé reste accessible par la page « Rejoindre »
    def test_quiz_prive_accessible_avec_le_code(self):
        self.page_accueil("omar")
        reponse = self.client.post("/rejoindre", data={"code_partage": "abc234"})
        self.assertEqual(reponse.status_code, 302)
        self.assertIn("code=ABC234", reponse.headers["Location"])

    # Sujet, difficulté et créateur sont affichés sur les cartes
    def test_sujet_difficulte_createur(self):
        page = self.page_accueil("omar")
        self.assertIn("Géographie", page)
        self.assertIn("difficulte-facile", page)
        self.assertIn("par maram", page)
        # Le quiz importé d'Omar : « par vous », sans badge de difficulté
        self.assertIn("par vous", page)
        self.assertNotIn("difficulte-difficile", page)


if __name__ == "__main__":
    unittest.main()
