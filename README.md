# Quiz App – PROJ531 (Groupe 4)

Plateforme web en Python (Flask) où chaque utilisateur peut créer ses propres quiz et jouer à ceux des autres.

## Fonctionnalités prévues
- Création de compte et connexion (mots de passe hachés)
- Chaque utilisateur peut créer ses quiz, manuellement ou depuis un fichier texte, et jouer à ceux des autres
- Le créateur d'un quiz en est l'administrateur : lui seul peut le modifier ou le supprimer
- Quiz publics (visibles par tous) ou privés (accessibles avec un code fourni par le créateur)
- Affichage du score final et des bonnes réponses
- Historique des scores de chaque utilisateur

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
- Planning, comptes-rendus et diagrammes : dossier `docs/comptes-rendus/`

## Arborescence
- `src/` : code source (application Flask)
- `data/` : fichiers d'exemple pour l'import de quiz
- `tests/` : tests
- `docs/` : documentation et comptes-rendus

## Format du fichier d'import
- Première ligne : `QUIZ:` suivi du titre
- Chaque question commence par `Q:`
- Une bonne réponse commence par `+`, une mauvaise par `-`
- Une ligne vide sépare deux questions

Exemples : `data/exemple_quiz.txt` (correct) et `data/exemple_quiz_erreur.txt` (avec erreurs).

## Installation et utilisation
1. Installer Python 3
2. Installer Flask : `pip install flask`
3. Lancer l'application : `cd src` puis `python app.py`
4. La page de connexion s'ouvre dans le navigateur (http://127.0.0.1:5000/login)
