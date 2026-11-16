# Quiz App – PROJ531 (Groupe 4)

Plateforme web en Python (Flask) où chaque utilisateur peut créer ses propres quiz et jouer à ceux des autres.

## Fonctionnalités prévues
- Création de compte et connexion (mots de passe hachés)
- Chaque utilisateur peut créer ses quiz et jouer à ceux des autres
- Trois façons de créer un quiz :
  - saisie directe dans un formulaire
  - import d'un quiz déjà écrit dans un fichier texte
  - génération automatique à partir d'un document (TXT ou PDF) grâce à une IA
- Chaque quiz a un thème et une difficulté (facile, moyen, difficile)
- Le créateur d'un quiz en est l'administrateur : lui seul peut le supprimer
- Quiz publics (visibles par tous) ou privés (accessibles avec un code de 6 caractères fourni par le créateur)
- Affichage du score final et des bonnes réponses
- Historique des scores de chaque utilisateur

## Règles des quiz
- 1 à 20 questions par quiz
- 2 à 6 réponses par question
- Une seule bonne réponse par question

## Équipe
| Membre | Rôle |
|---|---|
| Omar Hilali Najm | Product Owner |
| Sanda Ghozzi | Planificatrice / Scrum Master |
| Olivier De Rueda | Développeur données / comptes |
| Maram Bel-Houchet | Développeuse quiz / interface |

## Organisation
- Méthode : SCRUM (sprints de 1 à 2 séances) + diagramme de Gantt et PERT
- Suivi des tâches : Trello (lien disponible sur demande)
- Communication : Discord
- Une branche et une Pull Request relue par un autre membre pour chaque carte

## Arborescence
- `src/` : code source (application Flask)
- `data/` : fichiers d'exemple pour l'import de quiz et la génération par IA
- `tests/` : tests automatiques
- `docs/` : MCD et document d'architecture
- `docs/comptes-rendus/` : comptes-rendus de séance, planning des sprints, WBS, PBS, Gantt, PERT, grand bilan

## Format du fichier d'import
- Première ligne : `QUIZ:` suivi du titre
- Chaque question commence par `Q:`
- Une bonne réponse commence par `+`, une mauvaise par `-`
- Une ligne vide sépare deux questions

Exemples : `data/exemple_quiz.txt` (correct) et `data/exemple_quiz_erreur.txt` (avec erreurs).

## Installation et utilisation
1. Installer Python 3
2. Installer les dépendances : `pip install -r requirements.txt`
3. Lancer l'application : `cd src` puis `python app.py`
4. La page de connexion s'ouvre dans le navigateur (http://127.0.0.1:5000/login)

## Génération de quiz par IA (Groq)
1. Créer une clé gratuite sur https://console.groq.com/keys
2. Donner la clé à l'application, au choix :
   - variable d'environnement, dans le terminal qui lance l'application (à refaire à chaque nouveau terminal) :
     PowerShell `$env:GROQ_API_KEY="votre_clé"`, macOS/Linux `export GROQ_API_KEY="votre_clé"` ;
   - ou fichier `.env` à la racine du projet contenant `GROQ_API_KEY=votre_clé` (ignoré par git).

   Ne jamais mettre la clé dans le code ni la pousser sur GitHub.
3. Page « Importer » → « Générer à partir d'un document » (TXT ou PDF)

Documents de cours pour tester : `data/exemple_cours.txt` et `data/exemple_cours.pdf` (le système solaire).

Optionnel : `GROQ_MODEL=...` dans `.env` pour changer de modèle (par défaut `openai/gpt-oss-120b`, liste des modèles sur https://console.groq.com/docs/models).

**Plan B sans internet** : sans clé, sans connexion, ou si l'IA renvoie un quiz invalide, l'application génère des questions d'exemple (génération simulée) et affiche la raison. La page d'import marche donc toujours.

## Tests
Depuis la racine du projet : `python -m unittest discover tests`
