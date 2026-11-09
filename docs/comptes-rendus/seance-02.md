# Compte-rendu – Séance 2 (lundi 19/10/2026)

**Projet :** PROJ531 – Groupe 4 – Application Quiz Python (Flask)
**Durée :** 4 h
**Présents :** Omar Hilali Najm, Sanda Ghozzi, Olivier De Rueda, Maram Bel-Houchet
**Absents :** aucun
**Sprint :** Sprint 1 – Comptes utilisateurs et fondations (séances 2 et 3)

## Objectif de la séance

Démarrer le sprint 1 : faire fonctionner l'inscription et la connexion, poser les fondations (MCD, format d'import) et établir la planification du projet (Gantt, PERT, planning des sprints).

## Tâches achevées

| Tâche | Responsable | Temps estimé | Temps réel |
|---|---|---|---|
| Diagramme de Gantt et PERT (images + fichier draw.io) | Sanda | 2 h | … |
| Planning des sprints v2 (validé par le PO) | Sanda | 1 h | … |
| Compte-rendu de la séance 1 | Sanda | 0,5 h | … |
| Mise à jour du WBS et du PBS (interface Flask) | Sanda | – | … |
| Réorganisation du Trello (critères d'acceptation sur toutes les cartes, sprints) | Sanda | – | … |
| Format du fichier d'import + exemples (`exemple_quiz.txt`, `exemple_quiz_erreur.txt`) | Omar | 1 h | … *(poussé le 20/10 après la séance)* |

## Tâches commencées / incomplètes

| Tâche | Responsable | État en fin de séance |
|---|---|---|
| Corriger la connexion (+ critères inscription / connexion) | Olivier | **Partiel.** Requêtes SQL paramétrées : OK. Restent : table non créée au démarrage, vérification du mot de passe fausse, mots de passe non hachés. Les tables quiz / questions / réponses ont été créées en avance, avant le MCD. |
| MCD | Omar | **Non fait.** Rien dans le dépôt. |
| Import depuis un fichier texte | Maram | **Non fait.** Aucun commit depuis le 13/10. |
| Rapport – partie gestion de projet | Sanda | Non commencé, reporté. |

## Décisions prises

- **Fusion** : les cartes « Inscription » et « Connexion » sont fusionnées dans « Corriger la connexion à la base » (Olivier, 4 h).
- **Réattributions** (validées par le PO) : MCD → Omar ; Rôles → Omar ; Lister les quiz → Omar ; Création en saisie directe → Maram ; Page passage du quiz → Olivier ; Minuterie (bonus) → Olivier ; rapport final estimé à 12 h.
- **Rôle de Sanda** : Scrum Master, sans développement. Elle vérifie les critères d'acceptation avant qu'une carte passe en « Terminé ».
- **Pas de rôle admin global** : tout utilisateur peut créer des quiz et jouer à ceux des autres ; seul le créateur d'un quiz peut le modifier ou le supprimer. La carte « Distinction admin / joueur » devient « Droits du créateur ».
- **Quiz publics et privés** (priorité 5) : deux nouvelles cartes, « Choisir la visibilité du quiz » et « Accéder à un quiz privé par code » (code unique de 6 caractères).

## Problèmes rencontrés

Les bugs ci-dessous ont été constatés par le PO en lançant l'application (bilan du 23/10) :

| # | Gravité | Problème |
|---|---|---|
| B1 | Critique | Connexion impossible : la vérification du mot de passe compare un objet `sqlite3.Row` à une chaîne. |
| B2 | Critique | Erreur 500 sur une base neuve : les tables ne sont jamais créées au démarrage. |
| B3 | Majeur | Mots de passe enregistrés en clair. *Reporté au sprint 4 (carte « Sécurité : hachage + clé secrète »).* |
| B4 | Majeur | Erreur SQL dans `delete_utilisateur` (`DELETE * FROM`). |
| B5 | Majeur | Une base locale ancienne n'a pas la nouvelle colonne : chacun doit supprimer son `quizzapp.db`. |

Problèmes de conception relevés : le schéma de la base a été écrit **avant le MCD** (rôle global au lieu d'un créateur par quiz, score unique au lieu d'un historique, colonnes obligatoires absentes du format d'import, pas de clés étrangères, code des quiz privés non unique, règles du format d'import incomplètes).

Problèmes d'organisation : tout est poussé directement sur `main` sans relecture, messages de commit peu parlants, aucun test dans `tests/`, une carte considérée prête alors que ses critères n'étaient pas remplis, et du travail fait hors séance sans être noté dans Trello.

## Impact sur le planning

- Le **MCD** (3 h) est en retard. C'est le premier maillon du chemin critique : le projet a environ **3 h de retard**, à rattraper sur la marge du 23/11.
- La chaîne de Maram (import → erreurs → création → pages) prend aussi environ **3 h de retard**.

## Tâches à réaliser (séance 3 – 23/10)

| Priorité | Qui | Action | Fait quand… |
|---|---|---|---|
| 1 | Omar + Olivier | Trancher les problèmes de conception (créateur, scores, colonnes, clés étrangères, code unique) et faire le **MCD** avant de toucher à la structure quiz | MCD poussé dans `docs/`, schéma aligné dessus |
| 2 | Olivier | Corriger B1, B2, B4 et B5 ; ajouter `quizzapp.db` au `.gitignore` | Inscription → déconnexion → connexion fonctionne sur une base neuve ; la suppression de compte demande une simple confirmation « Êtes-vous sûr ? » |
| 3 | Maram | Pousser l'import en début de séance, même partiel, sur une branche | `exemple_quiz.txt` importé ; `exemple_quiz_erreur.txt` rejeté avec des messages clairs |
| 4 | Omar | Règles du format d'import dans le README ; `requirements.txt` | Fichiers présents sur `main` |
| 5 | Sanda | Compte-rendu de la séance 2, mise à jour du planning et du Trello (retards, nouvelles cartes), vérification des critères | `seance-02.md` poussé ; cartes Trello à jour |
| 6 | Toute l'équipe | Une branche par carte, une Pull Request relue par un autre membre avant fusion | Plus aucun commit direct sur `main` |

Les 2 h libres d'Omar en début de séance 3 sont à utiliser en priorité pour débloquer la chaîne de Maram.

*Mise à jour du 23/10 (PO) : la sécurité (hachage des mots de passe, clé secrète) est reportée en fin de projet, sur une carte dédiée au sprint 4. La suppression de compte se fait avec une simple confirmation, sans redemander le mot de passe.*
