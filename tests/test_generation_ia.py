# Tests de la génération de quiz par l'IA (Groq) et du plan B
# Groq est simulé : ces tests ne demandent ni internet ni clé.
# Lancement depuis la racine du dépôt : python -m unittest discover tests
import json
import os
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

import groq
import httpx

# Permet d'importer les modules du dossier src/
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "src"))

import generation_ia

# Document de cours utilisé dans les tests (assez long pour être envoyé à l'IA)
COURS = ("La Révolution française commence en 1789. La prise de la Bastille a lieu le 14 juillet 1789. "
         "La Déclaration des droits de l'homme et du citoyen est adoptée en août 1789.").encode("utf-8")

# Fausse requête HTTP, nécessaire pour créer les erreurs de la bibliothèque groq
REQUETE = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")


# Fausse réponse de Groq contenant "contenu" comme message de l'IA
def fausse_reponse(contenu):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=contenu))])


# Erreur renvoyée par Groq avec un code HTTP (401 : clé refusée, 429 : trop de demandes...)
def erreur_http(classe, code):
    return classe("erreur", response=httpx.Response(code, request=REQUETE), body=None)


# Quiz renvoyé par l'IA : nb questions, bonne réponse toujours en premier
def quiz_ia(nb):
    return json.dumps({
        "titre": "Révolution française",
        "questions": [
            {"texte": f"Question {i} ?", "choix": [f"Bonne {i}", "Faux A", "Faux B", "Faux C"], "reponse": 0}
            for i in range(nb)
        ],
    })


class TestGenerationIA(unittest.TestCase):
    def setUp(self):
        # Clé factice : on ne lit ni la vraie variable d'environnement ni le fichier .env
        patch_reglage = mock.patch.object(
            generation_ia, "lire_reglage", side_effect=lambda nom: "cle-test" if nom == "GROQ_API_KEY" else "")
        patch_reglage.start()
        self.addCleanup(patch_reglage.stop)

    # Lance la génération avec une fausse réponse de Groq (ou une erreur à lever).
    # Renvoie (quiz, raison, faux client) ; le faux client permet de vérifier ce qui a été envoyé.
    def generer(self, reponse_ou_erreur, nb_questions=3, contenu=COURS, extension=".txt"):
        faux_groq = mock.Mock()
        if isinstance(reponse_ou_erreur, Exception):
            faux_groq.return_value.chat.completions.create.side_effect = reponse_ou_erreur
        else:
            faux_groq.return_value.chat.completions.create.return_value = fausse_reponse(reponse_ou_erreur)
        with mock.patch.object(generation_ia.groq, "Groq", faux_groq):
            quiz, raison = generation_ia.generer_quiz(contenu, extension, "cours.txt", nb_questions)
        return quiz, raison, faux_groq

    # Réponse correcte de l'IA : le quiz est utilisé, sans plan B
    def test_quiz_genere_par_ia(self):
        quiz, raison, faux_groq = self.generer(quiz_ia(3))
        self.assertIsNone(raison)
        self.assertEqual(quiz["titre"], "Révolution française")
        self.assertEqual(len(quiz["questions"]), 3)
        # La bonne réponse reste la bonne après le mélange des réponses
        for i, question in enumerate(quiz["questions"]):
            self.assertEqual(question["choix"][question["reponse"]], f"Bonne {i}")
        # La clé est donnée au client Groq, et le texte du document est envoyé à l'IA
        self.assertEqual(faux_groq.call_args.kwargs["api_key"], "cle-test")
        envoi = faux_groq.return_value.chat.completions.create.call_args.kwargs
        self.assertIn("prise de la Bastille", envoi["messages"][0]["content"])
        self.assertEqual(envoi["response_format"], {"type": "json_object"})

    # Si l'IA renvoie trop de questions, on garde seulement le nombre demandé
    def test_questions_en_trop(self):
        quiz, raison, _ = self.generer(quiz_ia(8), nb_questions=5)
        self.assertIsNone(raison)
        self.assertEqual(len(quiz["questions"]), 5)

    # Plan B : pas d'internet
    def test_plan_b_sans_internet(self):
        quiz, raison, _ = self.generer(groq.APIConnectionError(request=REQUETE), nb_questions=4)
        self.assertIn("injoignable", raison)
        self.assertEqual(len(quiz["questions"]), 4)
        self.assertEqual(quiz["titre"], "cours")

    # Plan B : Groq ne répond pas à temps
    def test_plan_b_delai_depasse(self):
        _, raison, _ = self.generer(groq.APITimeoutError(request=REQUETE))
        self.assertIn("injoignable", raison)

    # Plan B : clé refusée par Groq
    def test_plan_b_cle_refusee(self):
        _, raison, _ = self.generer(erreur_http(groq.AuthenticationError, 401))
        self.assertIn("clé Groq est refusée", raison)

    # Plan B : trop de demandes (limite de la version gratuite)
    def test_plan_b_trop_de_demandes(self):
        _, raison, _ = self.generer(erreur_http(groq.RateLimitError, 429))
        self.assertIn("trop de demandes", raison)

    # Plan B : modèle retiré ou demande refusée
    def test_plan_b_autre_erreur(self):
        _, raison, _ = self.generer(erreur_http(groq.BadRequestError, 400))
        self.assertIn("code 400", raison)

    # Plan B : l'IA ne renvoie pas du JSON
    def test_plan_b_reponse_illisible(self):
        _, raison, _ = self.generer("Voici votre quiz : ...")
        self.assertIn("bon format", raison)

    # Plan B : quiz de l'IA invalide (une seule réponse, bonne réponse hors liste)
    def test_plan_b_quiz_invalide(self):
        mauvais = json.dumps({"titre": "X", "questions": [{"texte": "Q ?", "choix": ["A"], "reponse": 3}]})
        _, raison, _ = self.generer(mauvais)
        self.assertIn("incomplet", raison)

    # Plan B : document presque vide, Groq n'est même pas appelé
    def test_plan_b_document_trop_court(self):
        _, raison, faux_groq = self.generer(quiz_ia(3), contenu=b"Trop court.")
        self.assertIn("pas assez de texte", raison)
        faux_groq.assert_not_called()

    # Plan B : aucune clé configurée, Groq n'est pas appelé
    def test_plan_b_sans_cle(self):
        with mock.patch.object(generation_ia, "lire_reglage", return_value=""):
            _, raison, faux_groq = self.generer(quiz_ia(3))
        self.assertIn("aucune clé", raison)
        faux_groq.assert_not_called()

    # Plan B : PDF illisible
    def test_plan_b_pdf_illisible(self):
        _, raison, faux_groq = self.generer(quiz_ia(3), contenu=b"%PDF-1.4 fichier casse", extension=".pdf")
        self.assertIsNotNone(raison)
        faux_groq.assert_not_called()


if __name__ == "__main__":
    unittest.main()
