# Compte-rendu – Séance 3 (vendredi 23/10/2026)

**Projet :** PROJ531 – Groupe 4 – Application Quiz Python (Flask)
**Durée :** 4 h
**Présents :** Omar Hilali Najm, Sanda Ghozzi, Olivier De Rueda, Maram Bel-Houchet
**Absents :** aucun
**Sprint :** fin du Sprint 1 – Comptes utilisateurs et fondations
**Sources :** dépôt GitHub, Trello, bilan de la séance 2 et grand bilan du projet (02/11)

## Objectif de la séance

Rattraper les retards de la séance 2 (MCD, connexion, import), trancher les questions de conception et mettre en place les règles de travail (branches, relecture, vérification des critères).

## Tâches achevées

| Tâche | Responsable | Temps estimé | Temps réel |
|---|---|---|---|
| Correction de la connexion : inscription, connexion et déconnexion fonctionnent sur une base neuve | Maram (carte d'Olivier) | 4 h | … |
| Suppression de compte avec une simple confirmation | *à préciser* | – | … |
| Interface : création de quiz, quiz privés avec code, minuteur, passage du quiz et score | Maram | – | … |
| Choisir la visibilité du quiz | Maram | 2 h | 1 h 40 |
| Minuterie sur un quiz (bonus) | Maram | 4 h | 30 min |
| MCD – Prototype 1 (`docs/`) | Omar | 3 h | … |
| Document d'architecture (`docs/`) | Maram (déposé par Omar) | – | … |
| README : règles des quiz, format d'import, installation, tests | Omar | 0,5 h | … |
| Compte-rendu de la séance 2 | Sanda | 0,5 h | … |
| Planning v3 (Gantt, PERT, planning des sprints) | Sanda | – | … |
| Trello : critères mis à jour, colonne « En revue », première vérification des critères | Sanda | – | … |

## Tâches en revue (faites, en attente de fusion)

| Tâche | Responsable | État |
|---|---|---|
| Import d'un quiz depuis un fichier texte + erreurs d'import + page « Importer » | Maram | Pull Request n°2 (branche `import-fichier-texte`), **16 tests automatiques**. `exemple_quiz.txt` importé ; `exemple_quiz_erreur.txt` refusé avec 3 erreurs et leurs numéros de ligne. Code privé à 6 caractères. Non fusionnée. |

## Tâches incomplètes

| Tâche | Responsable | État en fin de séance |
|---|---|---|
| Tables alignées sur le MCD | Olivier | Schéma partagé sur Discord, **pas envoyé sur GitHub** |
| Création d'un quiz en saisie directe | Maram | Fonctionne sur la table de test, mais le formulaire est limité à 3 réponses (règle : 2 à 6) |
| Droits du créateur | Omar | Non commencé : attend le créateur dans les vraies tables |
| README : `requirements.txt` | Omar | Règles écrites ; fichier `requirements.txt` absent |

## Décisions prises

- **Sécurité** (hachage des mots de passe, clé secrète) reportée au dernier sprint, sur une carte dédiée.
- **Suppression de compte** : une simple confirmation « Êtes-vous sûr ? », sans redemander le mot de passe.
- **Règles des quiz** : 1 à 20 questions, 2 à 6 réponses par question, une seule bonne réponse.
- **Code des quiz privés** : 6 caractères, sans les caractères qu'on confond (0/O, 1/I/L).
- **Génération de quiz à partir d'un document** via une IA gratuite (Groq), sous réserve de l'accord d'Olivier. Elle ne démarre qu'après l'historique et la correction détaillée.
- **Organisation** : une branche par carte, une Pull Request relue par un autre membre avant fusion. Une carte passe en « Terminé » seulement quand sa PR est fusionnée et que la Scrum Master a vérifié ses critères (nouvelle colonne « En revue » dans Trello).

## Problèmes rencontrés

- **Deux modèles de quiz en parallèle** : l'interface enregistre les quiz dans une table de test (`quizzes`, questions en JSON), alors que le MCD prévoit des tables quiz / questions / réponses. Les droits du créateur, l'historique et la correction détaillée en dépendent.
- **Travail fait mais non envoyé** : le schéma d'Olivier est resté sur Discord.
- **Pull Requests ouvertes sans relecture ni fusion.** La branche de la PR n°1 (`SinisterOlivier-patch-1`) part de la version du 19/10 : la fusionner telle quelle supprimerait le travail ajouté depuis. Il faut la refaire à partir de `main`.
- **Temps réels** non renseignés dans Trello pour la plupart des cartes.
- **Fichiers mal rangés** : une copie du PERT à la racine du dépôt (`PERT_Application_Quiz (3).drawio`) et deux images mal nommées dans `docs/comptes-rendus/`.

## Suivi depuis la séance (vacances, 23/10 – 02/11)

Aucun travail envoyé sur GitHub pendant les vacances. Le retard sur la base de données (environ une séance) n'a pas été rattrapé.

## Tâches à réaliser (séance 4 – 02/11)

| Priorité | Qui | Action | Fait quand… |
|---|---|---|---|
| 1 | Olivier | Envoyer les tables alignées sur le MCD, sur une nouvelle branche partie de `main` | PR relue et fusionnée ; plus de table de test pour les nouvelles fonctionnalités |
| 2 | Omar + Maram | Relire et fusionner la PR n°2 (import + tests) | Import disponible sur `main`, 16 tests qui passent |
| 3 | Maram + Olivier | Commencer le branchement de l'interface sur les vraies tables | Création et liste des quiz utilisent les tables du MCD |
| 4 | Omar | Droits du créateur ; `requirements.txt` | Seul le créateur modifie ou supprime son quiz ; fichier présent |
| 5 | Maram | Formulaire de création : 2 à 6 réponses | Règle du README respectée |
| 6 | Sanda | Compte-rendu S3, planning v4, Trello, rangement de `docs/`, vérification des critères, partie gestion de projet du rapport | Fichiers sur GitHub, cartes à jour |
| 7 | Toute l'équipe | Renseigner les temps réels de ses cartes à la fin de chaque séance | Plus de carte « Terminé » sans temps réel |
