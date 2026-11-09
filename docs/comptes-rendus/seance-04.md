# Compte-rendu – Séance 4 (lundi 02/11/2026)

**Projet :** PROJ531 – Groupe 4 – Application Quiz Python (Flask)
**Durée :** 4 h
**Présents :** Omar Hilali Najm, Sanda Ghozzi, Olivier De Rueda, Maram Bel-Houchet
**Absents :** aucun
**Sprint :** Sprint 2 – Base commune
**Sources :** point PO du 09/11 (bilan de la séance 4), historique du dépôt GitHub, Trello

## Objectif de la séance

Rattraper la séance de retard sur la base de données : tables alignées sur le MCD, fusion de l'import (PR n°2), branchement de l'interface sur les vraies tables, droits du créateur.

## Ce que chacun a fait

| Membre | Travail réalisé | Temps estimé | Temps réel |
|---|---|---|---|
| Olivier | Nouvelles tables proches du MCD : créateur, origin, thème, difficulté, `attempts` avec `id_quizz`, table des documents. Fonctions de `app.py` réécrites pour la nouvelle base. **Envoyé directement sur `main`, sans Pull Request.** | 2 h + 2 h | … |
| Maram | Trois branches et trois PR (n°3, n°4, n°5). La **PR n°5** reprend les deux autres : interface adaptée à la nouvelle base, création de quiz complète avec les règles du README (2 à 6 réponses, 20 questions, 1 bonne réponse), code à 6 caractères, accès par code réparé | 1 h + 2 h | … |
| Omar (PO) | Relecture et test de toutes les branches ; MCD mis à jour avec le thème ; `requirements.txt` ; README mis à jour (installation, thème et difficulté) | 0,5 h | … |
| Sanda | Compte-rendu de la séance 3, planning v4 (validé par le PO), nouveaux PERT et Gantt, rangement complet de `docs/` (noms, doublons, image du PERT) ; Trello aligné sur le grand bilan | – | … |

## Non réalisé à la séance 4

- **Aucune Pull Request fusionnée** (5 PR ouvertes).
- Droits du créateur.
- Adaptation de l'import (PR n°2), écrit pour l'ancienne table.
- Clés étrangères sur `attempts` et sur la table des documents.
- Compte-rendu de la séance 4.

## Problèmes rencontrés

- **Envoi direct sur `main` sans Pull Request** : l'application a d'abord planté au démarrage, puis n'a été corrigée qu'en partie. `main` est resté cassé jusqu'au 09/11 : accueil en erreur, quiz créés sans questions, accès par code impossible.
- **Travail prêt mais pas fusionné** : la PR n°5, testée par le PO, fonctionnait, mais personne ne l'a fusionnée.
- **Aucun envoi entre le 02/11 (18h40) et le 09/11.**
- **Temps réels** non renseignés sur la plupart des cartes terminées.

## Décisions prises

- **Planning v4 validé** par le PO.
- **Sécurité** avancée au 16/11, si Olivier a le temps.
- **PR n°1** à ne pas fusionner : sa branche part de la version du 19/10.

## Suivi : début de la séance 5 (09/11)

**Décisions du PO (point du 09/11) :**
- Terminer d'abord la séance 4, sinon personne ne peut avancer.
- **Origin** d'un quiz créé à la main : « saisie », pour rester cohérent avec le MCD.
- **Génération par IA** : gardée seulement si l'historique est terminé le 16/11 ; sinon, elle ira dans les « améliorations possibles » du rapport.
- Fermer les PR n°1, n°3 et n°4 sans les fusionner.
- Plus aucun envoi direct sur `main` : une branche et une PR relue pour chaque carte, validée par le PO après test.

**Réalisé :**
- **14h22** – PR n°5 fusionnée par Olivier. `main` fonctionne de nouveau (testé par Omar).
- Omar ajoute le thème au MCD (`docs/`) et ouvre la PR `droits-createur` : route de suppression réservée au créateur, bouton « Supprimer » visible seulement par lui, page et lien Admin supprimés.
- Cartes passées en « Terminé » : tables, interface branchée, formulaire de création.

## Tâches à réaliser (séance 5 – 09/11, suite)

| Ordre | Qui | Action | Fait quand… |
|---|---|---|---|
| 1 | Olivier | Fermer les PR n°1, n°3 et n°4 | Il ne reste que les PR utiles |
| 2 | Olivier | Enregistrer les scores dans `attempts`, puis afficher l'historique, sur une branche avec PR | Chaque tentative est enregistrée (quiz, score, date) |
| 2 | Maram | Adapter la PR n°2 (import) à la nouvelle base, origin « saisie », la faire fusionner | `exemple_quiz.txt` importé et `exemple_quiz_erreur.txt` refusé sur `main` ; les 16 tests passent |
| 2 | Omar | Droits du créateur (PR `droits-createur`), puis correction détaillée | Seul le créateur peut supprimer son quiz, même par l'URL |
| 2 | Sanda | Comptes-rendus des séances 4 et 5, planning v5, Trello avec les temps réels, rapport partie gestion de projet | Fichiers sur GitHub, cartes à jour |
