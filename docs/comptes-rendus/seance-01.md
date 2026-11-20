# Compte-rendu – Séance 1 (mardi 13/10/2026)

**Projet :** PROJ531 – Groupe 4 – Application Quiz Python
**Durée :** 4 h
**Présents :** Omar Hilali Najm, Sanda Ghozzi, Olivier De Rueda, Maram Bel-Houchet
**Absents :** aucun

## Rôles

| Membre | Rôle |
|---|---|
| Omar Hilali Najm | Product Owner |
| Sanda Ghozzi | Scrum Master / planificatrice |
| Olivier De Rueda | Base de données (SQLite, MCD) |
| Maram Bel-Houchet | Interface Flask, création de quiz |

## Objectif de la séance

Mettre en place le projet (dépôt, outils, organisation) et démarrer un premier prototype.

## Tâches achevées

| Tâche | Responsable | Temps estimé | Temps réel |
|---|---|---|---|
| Création du dépôt GitHub, arborescence (`src/`, `data/`, `tests/`, `docs/`) et README | Omar | 1 h | 40 min |
| Création du tableau Trello et du backlog (23 tâches) | Sanda | 1 h | 1 h 10 |
| WBS et PBS (draw.io), déposés dans `docs/` | Sanda | 2 h | 1 h 40 |
| Prototype Flask : pages connexion, inscription et accueil, gabarit commun et feuille de style | Maram | 3 h | 3 h |

10 commits envoyés pendant la séance.

## Tâches commencées / incomplètes

| Tâche | Responsable | État en fin de séance |
|---|---|---|
| Branchement de SQLite pour les comptes | Olivier | Commencé pendant la séance, envoyé le 14/10 |
| Choix du stockage et du format du fichier d'import | Équipe | Format d'import non encore défini |
| Gantt / PERT et planning des sprints | Sanda | Reportés : dates des séances à demander à l'enseignant |

## Tâches à réaliser (séance 2 – 19/10)

- Faire fonctionner l'inscription et la connexion avec SQLite (Olivier)
- MCD et table utilisateur avec rôle (Olivier)
- Rôles admin / joueur (Omar)
- Définir le format du fichier d'import et mettre des exemples dans `data/` (Omar)
- Gantt / PERT et planning des sprints (Sanda)
- Compléter le README : `requirements.txt` et instructions d'installation (Omar)
- Retirer le lien d'invitation Trello du README, le dépôt étant public (Omar)
- Ajouter `quizzapp.db` au `.gitignore` (Olivier)

## Décisions prises

- Rôles attribués (voir le tableau ci-dessus).
- Outils : GitHub pour le code, Trello pour le suivi des tâches (colonnes Backlog, En cours, Terminé), Discord pour la communication.
- Interface développée avec Flask.
- Pour chaque tâche, on note le temps estimé et le temps réel dans la carte Trello.

## Problèmes rencontrés

- Aucun problème bloquant pendant la séance.
- Les dates des séances n'étaient pas encore connues, ce qui a reporté le Gantt et le planning des sprints.

## Suivi depuis la séance (14/10 – 19/10)

- **14/10** – Olivier branche SQLite : l'inscription et la connexion renvoient une erreur 500.
- **19/10** – Olivier corrige le plantage et sécurise les requêtes SQL (paramètres « ? »). Il reste trois corrections avant de valider la carte « Corriger la connexion à la base » : créer la table au démarrage, corriger la vérification du mot de passe à la connexion, et hacher les mots de passe.
