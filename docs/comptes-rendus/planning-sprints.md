# Planning des sprints – Application Quiz Python

**Groupe 4 – PROJ531** · Version 2 du 19/10/2026 (validée par le PO, avec ses ajustements)

## Hypothèses

- 7 séances de 4 h : 13/10, 19/10, 23/10, 02/11, 09/11, 16/11 et 23/11.
- Pas de travail en dehors des séances et pas d'absence prévue.
- Développement : Omar, Olivier et Maram. Sanda (Scrum Master) ne code pas : elle gère la planification, vérifie les critères d'acceptation, rédige les comptes-rendus et la partie gestion de projet du rapport.
- La démonstration a lieu à la dernière séance (23/11). *À confirmer avec l'enseignant.*
- Rapport final : 12 h au total (6 h pour la partie gestion de projet, 2 h par développeur pour la partie produit et la démo).

## Changements par rapport à la version 1

| Changement | Décision |
|---|---|
| « Inscription » et « Connexion » fusionnées dans « Corriger la connexion à la base » (Olivier) | Proposé par le PO : même travail. Estimation passée à 4 h. |
| MCD : Olivier → Omar | Validé par le PO |
| Page passage du quiz et score : Omar → **Olivier** | Sanda ne code pas ; Olivier est le développeur le plus disponible à ce moment-là |
| Minuterie (bonus) : Omar → Olivier | Validé par le PO |
| Rapport final : 6 h → 12 h | Validé par le PO |

## Vue d'ensemble

| Sprint | Séance(s) | Objectif | Livré en fin de sprint |
|---|---|---|---|
| **Sprint 0** | 13/10 | Mise en place | Dépôt, Trello, WBS/PBS, prototype Flask ✅ |
| **Sprint 1** | 19/10 – 23/10 | **Comptes utilisateurs** + fondations | Inscription et connexion validées (19/10), rôles admin / joueur, MCD, structures utilisateur et quiz, import de fichier avec gestion des erreurs |
| **Sprint 2** | 02/11 | **Création de quiz** | Création d'un quiz en saisie directe, liste des quiz, enregistrement des scores |
| **Sprint 3** | 09/11 | **Passage de quiz** | Questions / réponses, page de passage, pages de création et d'import, affichage de l'historique |
| **Sprint 4** | 16/11 – 23/11 | **Historique, tests, démo** | Score et correction, page historique, tests, rapport, démonstration |

## Chemin critique (PERT)

**MCD → Structure quiz → Lister les quiz → Questions / réponses → Score et correction → Tests → Rapport + démo**

Il représente 17 h de travail, soit un peu plus de 4 séances sur les 6 restantes. Ce sont surtout les tâches d'**Omar** qu'il faut surveiller : un retard sur l'une d'elles retarde toute la fin du projet. La séance du 23/11 sert de marge de sécurité.

## Détail séance par séance

### Sprint 1 – Comptes utilisateurs et fondations

#### Séance 2 – 19/10
| Membre | Travail prévu |
|---|---|
| Omar | Format du fichier d'import + exemples dans `data/` (1 h) ; MCD (3 h) |
| Olivier | Corriger la connexion, avec les critères d'inscription et de connexion (4 h) |
| Maram | Import depuis un fichier texte (3 h) ; 1 h libre |
| Sanda | Gantt / PERT (2 h) ; planning des sprints (1 h) ; compte-rendu (0,5 h) ; rapport partie B (0,5 h) |

#### Séance 3 – 23/10
| Membre | Travail prévu |
|---|---|
| Omar | Rôles admin / joueur (2 h) ; 2 h libres en début de séance, en attendant la table utilisateur : README (`requirements.txt`, installation) ou début des gabarits HTML des pages de création / import |
| Olivier | Table utilisateur avec rôle (2 h) ; structure quiz / question / réponses (2 h) |
| Maram | Fin de l'import (1 h) ; erreurs d'import (2 h) ; 1 h libre |
| Sanda | Vérification des critères (1 h) ; rapport partie B (2,5 h) ; compte-rendu (0,5 h) |

### Sprint 2 – Création de quiz

#### Séance 4 – 02/11
| Membre | Travail prévu |
|---|---|
| Omar | Lister les quiz (2 h) ; questions / réponses (2 h) |
| Olivier | Enregistrer le score (2 h) ; page passage du quiz et score (2 h) |
| Maram | Création d'un quiz en saisie directe (4 h) |
| Sanda | Vérification des critères (1 h) ; rapport partie B (2,5 h) ; compte-rendu (0,5 h) |

### Sprint 3 – Passage de quiz

#### Séance 5 – 09/11
| Membre | Travail prévu |
|---|---|
| Omar | Fin des questions / réponses (2 h) ; score et correction (2 h) |
| Olivier | Fin de la page passage (2 h) ; afficher l'historique (2 h) |
| Maram | Pages création et import de quiz (4 h) |
| Sanda | Vérification des critères (1 h) ; rapport partie B (0,5 h) ; compte-rendu (0,5 h) ; 2 h libres |

### Sprint 4 – Historique, tests et démo

#### Séance 6 – 16/11
| Membre | Travail prévu |
|---|---|
| Omar | Fin du score (1 h) ; tests (1 h) ; rapport partie produit (1 h) |
| Olivier | Page historique (2 h) ; tests (1 h) ; rapport partie produit (1 h) |
| Maram | Export JSON – bonus (2 h) ; tests (1 h) ; rapport partie produit (1 h) |
| Sanda | Vérification finale des critères (1 h) ; compte-rendu (0,5 h) ; relecture du rapport |

#### Séance 7 – 23/11
| Membre | Travail prévu |
|---|---|
| Toute l'équipe | Fin du rapport (1 h par développeur) ; **démonstration finale** ; marge pour rattraper un éventuel retard |
| Sanda | Dernier compte-rendu |

## Points d'attention

- **Pages création / import (Maram)** : elles se terminent au sprint 3 et non au sprint 2. La chaîne import → erreurs → création → pages représente 14 h pour une seule personne, soit 3,5 séances. Pour les avancer, Omar peut commencer les gabarits HTML pendant ses 2 h libres du 23/10.
- **Minuterie (bonus)** : elle n'entre pas dans le planning. On ne la fera que si le projet prend de l'avance.
- **Chemin critique** : si une tâche d'Omar prend du retard, Maram ou Olivier (1 à 2 h libres certaines séances) viennent l'aider à la séance suivante.

## Suivi

À chaque fin de séance : mise à jour du Trello (cartes déplacées, temps réel), compte-rendu sur GitHub, comparaison de l'avancement avec ce planning.
