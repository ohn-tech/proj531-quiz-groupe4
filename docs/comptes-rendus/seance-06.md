# Compte-rendu – Séance 6 (lundi 16/11/2026)

**Projet :** PROJ531 – Groupe 4 – Application Quiz Python (Flask)
**Durée :** 4 h
**Présents :** Omar Hilali Najm, Olivier De Rueda, Maram Bel-Houchet
**Absents :** Sanda Ghozzi
**Sprint :** Sprint 4 – Historique, IA, sécurité (dernière séance de développement avant la présentation du 23/11)
**Sources :** historique du dépôt GitHub (commits et Pull Requests n°12 à n°22), compte-rendu et bilan du PO, planning des sprints v6

## Objectif de la séance

Livrer toutes les fonctionnalités restantes (correction détaillée, historique, génération par IA, clés étrangères, sécurité), tester l'application complète et geler le code avant la présentation.

## Ce que chacun a fait

| Membre | Travail réalisé | Temps estimé | Temps réel |
|---|---|---|---|
| Omar (PO) | Correction détaillée : après un quiz, chaque question affiche la réponse donnée, « Juste » ou « Faux » et la bonne réponse (**PR n°12**, fusionnée à 16h05) | 1,5 h | … |
| Omar (PO) | Finitions de la page historique : statistiques (quiz passés, moyenne, meilleur résultat), date lisible, score en %, lien « Rejouer » (**PR n°16**, fusionnée à 16h36) | 2 h | … |
| Omar (PO) | README final (fonctionnalités, installation, `SECRET_KEY`, partie sécurité) ; test de chaque PR sur une base neuve, ordre de fusion, gel du code | – | … |
| Maram | Génération de quiz par IA avec Groq à partir d'un TXT ou d'un PDF, clé dans une variable d'environnement, plan B sans clé ou sans internet, 12 tests (**PR n°14**, fusionnée à 16h36) | 4 h | … |
| Maram | Accueil plus présentable : en-tête, tuiles d'action, badge « Quiz public » (**PR n°15**, 16h37) ; création de quiz dans une fenêtre par-dessus l'accueil (**PR n°18**, 17h04) | – | … |
| Maram | Documents de cours d'exemple `data/exemple_cours.txt` et `.pdf`, testés avec une vraie clé Groq (**PR n°19**, 17h19) ; accueil limité aux vrais quiz de la base (**PR n°22**, 17h50) | – | … |
| Maram | Changement de modèle Groq (l'ancien renvoyait une erreur 404) : `openai/gpt-oss-120b`, avec un message clair si ça se reproduit | – | … |
| Maram | Rapport : partie interface, import, IA et tests | – | … |
| Olivier | Sécurité : mots de passe hachés (werkzeug), clé secrète lue dans `SECRET_KEY`, clés étrangères sur `attempts`, `folder` et le créateur du quiz, suppression de compte avec ses quiz et tentatives, suppression des comptes de test (**PR n°17**, fusionnée à 16h51) | 1 h + 1 h | … |
| Olivier | Ménage : suppression de `bientot.html` et `tests_db.py`, inutilisés (**PR n°20**, 17h20) ; code de partage `UNIQUE` dans la table `quizz` (**PR n°21**, 17h40) | – | … |
| Olivier | Rapport : partie back-end, base de données et sécurité | – | … |

**État final de `main`**, testé par le PO sur une base neuve avec deux comptes : inscription et connexion (mots de passe hachés), création, import, génération par IA (et plan B), quiz privé rejoint par code, passage avec minuteur, correction détaillée, historique avec statistiques, suppression d'un quiz par son créateur uniquement, suppression de compte. **34 tests automatiques OK. Toutes les fonctionnalités du backlog sont livrées.**

## Non réalisé à la séance 6

| Tâche | Responsable | État en fin de séance |
|---|---|---|
| Comptes-rendus des séances 5 et 6 | Sanda | Rédigés après la séance |
| Temps réels dans Trello | Tous | À envoyer à Sanda |
| Test du parcours complet sur chaque PC Windows | Tous | Commencé en fin de séance |
| Rapport final | Omar, Sanda | Parties de Maram et d'Olivier rendues le 16/11 ; parties d'Omar et de Sanda à rédiger, puis assemblage |

## Problèmes rencontrés

- **PR n°13 (sécurité, 1re version)** : l'application ne démarrait plus (`add_utilisateurs()` appelée sans argument) et la suppression de compte renvoyait une erreur 500 à cause des nouvelles clés étrangères. Fermée.
- **PR n°17 (1re version)** : basée sur un ancien `app.py`, elle aurait effacé l'IA, la correction détaillée et l'historique. Refaite sur le `main` actuel avant la fusion.
- **Conflit** entre la sécurité et l'IA sur les imports en haut de `app.py` : les deux lignes ont été gardées.
- **Quiz d'exemple absents de l'historique** : corrigé par la PR n°22.
- **Fichiers déposés avec « (1) » / « (2) » dans le nom** sur la branche des droits : supprimés et redéposés avec le bon nom.

## Décisions prises

- Plus de comptes de test (admin/admin, maram/1234) : aucun compte n'existe au départ, on s'inscrit.
- Code de partage `UNIQUE` dans la base, en plus de la vérification faite par l'application.
- L'accueil n'affiche que les vrais quiz : les quiz d'exemple écrits dans le code n'étaient pas enregistrés dans la base, leurs résultats ne pouvaient donc pas aller dans l'historique.
- **Gel du code à 17h30** : plus aucune fusion sauf pour corriger un bug. Seule la PR n°22 (correction de bug) a été fusionnée ensuite.
- Ordre de fusion : IA (n°14), puis historique (n°16), puis accueil (n°15), puis sécurité (n°17) une fois corrigée.
- Après la mise à jour, chacun supprime son `src/quizzapp.db` pour repartir d'une base propre.

## Impact sur le planning

- Le sprint 4 est terminé en une séance au lieu de deux : la sécurité, prévue jusqu'au 23/11, est livrée le 16/11.
- Les tests, prévus au début du 23/11, sont faits dès le 16/11 (34 tests OK) ; il reste le test sur chaque PC.
- Le 23/11 est entièrement consacré à la présentation et à la démonstration.

## Tâches à réaliser (avant la présentation du 23/11)

| Priorité | Qui | Action | Fait quand… |
|---|---|---|---|
| 1 | Tous | Tester le parcours complet sur son PC avec le dernier ZIP de `main` et une base neuve | Aucun bug sur Windows ; Maram vérifie l'IA avec sa clé |
| 1 | Tous | Envoyer ses temps réels à Sanda | Trello complet, prévu / réel comparable |
| 2 | Sanda | Déposer les comptes-rendus 5 et 6 ; Trello à jour ; partie gestion de projet du rapport | Fichiers sur GitHub |
| 2 | Omar | Rapport : vision produit, backlog, décisions, bilan et améliorations possibles ; assemblage du rapport | Rapport complet |
| 3 | Tous | Préparer la présentation et la démonstration (avec plan B sans internet) | Répétition faite avant le 23/11 |
