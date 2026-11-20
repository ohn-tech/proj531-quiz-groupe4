# Compte-rendu – Séance 5 (lundi 09/11/2026)

**Projet :** PROJ531 – Groupe 4 – Application Quiz Python (Flask)
**Durée :** 4 h
**Présents :** Omar Hilali Najm, Sanda Ghozzi, Olivier De Rueda, Maram Bel-Houchet
**Absents :** aucun (Sanda arrivée avec environ 20 min de retard)
**Sprint :** fin du Sprint 2 (base commune), puis Sprint 3 – Fin de la base et passage de quiz
**Sources :** historique du dépôt GitHub (commits et Pull Requests), point PO du 09/11, planning des sprints v6

## Objectif de la séance

Terminer d'abord la séance 4 (aucune Pull Request fusionnée le 02/11, `main` cassé), puis livrer les fonctionnalités principales du sprint 3 : import branché sur la base, liste des quiz, droits du créateur, enregistrement des scores et historique.

## Ce que chacun a fait

| Membre | Travail réalisé | Temps estimé | Temps réel |
|---|---|---|---|
| Maram | Interface branchée sur la nouvelle base + création de quiz avec les règles (**PR n°5**, fusionnée à 14h22 par Olivier) : `main` fonctionne de nouveau | – | *compté à la séance 4* |
| Maram | Import d'un quiz depuis un fichier texte adapté à la nouvelle base, origin « import » (**PR n°2**, fusionnée à 16h51) ; 16 tests OK | 1,5 h | 4 h *(carte complète, 23/10 + 09/11)* |
| Maram | Origin « saisie » pour les quiz créés avec le formulaire | – | *inclus dans l'import* |
| Maram | Liste des quiz : sujet, difficulté, créateur, nombre de questions sur les cartes + 6 tests (**PR n°10**, fusionnée à 17h57) | – | 1 h 30 |
| Maram | `*.db` ajouté au `.gitignore` ; génération par IA commencée sur la branche `generation-ia` | – | *inclus dans l'IA (séance 6)* |
| Omar (PO) | Droits du créateur : seul le créateur voit le bouton « Supprimer » et peut supprimer son quiz, même par l'adresse (**PR n°11**, fusionnée à 18h15) | 2 h | 2 h 30 |
| Omar (PO) | Test de chaque Pull Request sur une base neuve, choix de l'ordre de fusion (n°2 → n°10 → n°11 → n°9) ; bilan global du projet et bilan de la séance 4 | 0,5 h | *inclus dans « Tests » : 3 h sur les 09/11 et 16/11* |
| Olivier | Enregistrement des scores dans `attempts` (date et heure à la seconde) + fonction `historique_utilisateur` au format défini par Maram + page historique (**PR n°9**, fusionnée à 18h15) | 2 h + 1 h | 2 h + 1 h |
| Omar, Olivier | Fermeture sans fusion des PR obsolètes n°1, 3, 4, 6, 7 et 8 | – | – |
| Sanda | Compte-rendu de la séance 4, planning v5 puis v6 (IA obligatoire, export JSON abandonné), PERT et Gantt mis à jour, Trello mis à jour ; question au PO sur le critère « modifier » de la carte Droits du créateur → critère limité à la suppression, carte « Amélioration possible : modifier un quiz » créée | 1,5 h | 3 h |

**État de `main` en fin de séance**, testé par le PO sur une base neuve : inscription, connexion, création, import, quiz privé avec code, passage d'un quiz, score enregistré, historique affiché, suppression d'un quiz par son créateur uniquement, suppression de compte. **22 tests automatiques OK.**

## Non réalisé à la séance 5

| Tâche | Responsable | État en fin de séance |
|---|---|---|
| Correction détaillée | Omar | Non commencée, reportée au 16/11 |
| Clés étrangères sur `attempts`, la table des documents et le créateur du quiz | Olivier | Reportée au 16/11 |
| Compte-rendu de la séance 5 | Sanda | Rédigé après la séance |
| Temps réels dans Trello | Tous | Peu renseignés |

## Problèmes rencontrés

- **PR n°7 et n°8 (Olivier)** : construites à partir de l'ancien `app.py` du 02/11, elles auraient effacé le travail de Maram (règles, code à 6 caractères, formulaire). Fermées ; la PR n°9, repartie du `main` actuel, a été fusionnée.
- **Première version des droits du créateur (PR n°6)** en conflit avec l'import : refaite sur le `main` à jour (PR n°11).
- **Page historique manquante** dans la première version de la PR n°9 : ajoutée par Olivier avant la fusion.
- Fichier déposé sur une branche déjà existante ; noms de fichiers à vérifier avant chaque dépôt.

## Décisions prises

- Terminer la séance 4 avant tout le reste : fusion de la PR n°5 en priorité.
- **Plus aucun envoi direct sur `main`** : une branche par tâche, partie du `main` actuel, une Pull Request testée par le PO avant fusion.
- **Origin** d'un quiz : « saisie » (formulaire) ou « import » (fichier), pour rester cohérent avec le MCD.
- **Génération par IA obligatoire** (décision du PO à 16h) : Maram s'en charge le 16/11, avec un plan B sans internet. Maram proposait de confier l'appel à Groq à Olivier ; le PO confie toute la génération à Maram.
- **Export JSON** (bonus) abandonné, passe en « amélioration possible ».
- **Page historique** : Maram → Omar, pour libérer Maram pour l'IA.
- **Liste des quiz** : Omar → Maram, qui avait déjà construit l'accueil.
- Les PR obsolètes sont fermées sans fusion.
- **Droits du créateur** : le critère ne couvre que la suppression ; « modifier un quiz » devient une amélioration possible.
- **Date des tentatives** : date et heure complètes à la seconde, au même format que `date_quizz`, pour trier l'historique.

## Impact sur le planning

- Le retard de la séance 4 est rattrapé : toutes les tâches du sprint 3 prévues pour le 09/11 sont fusionnées le jour même.
- La séance du 16/11 est pleine pour Omar et Maram (correction détaillée, historique, IA). Les tests passent au début du 23/11.

## Tâches à réaliser (séance 6 – 16/11)

| Priorité | Qui | Action | Fait quand… |
|---|---|---|---|
| 1 | Maram | Génération de quiz par IA avec Groq + plan B sans internet ; `groq` dans `requirements.txt` ; clé jamais sur GitHub | Un document TXT ou PDF produit un quiz ; sans clé, le plan B fonctionne |
| 1 | Omar | Correction détaillée, puis finitions de la page historique | Après un quiz, chaque question affiche la réponse donnée et la bonne réponse |
| 1 | Olivier | Clés étrangères, puis sécurité (hachage des mots de passe, clé secrète) | Mots de passe hachés, clé secrète hors du code, suppression de compte fonctionnelle |
| 2 | Sanda | Comptes-rendus des séances 5 et 6, Trello avec les temps réels, partie gestion de projet du rapport | Fichiers sur GitHub, cartes à jour |
