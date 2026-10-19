# Planning des sprints – Application Quiz Python

**Groupe 4 – PROJ531** · Version du 19/10/2026

## Hypothèses

- 7 séances de 4 h : 13/10, 19/10, 23/10, 02/11, 09/11, 16/11 et 23/11.
- Pas de travail en dehors des séances et pas d'absence prévue.
- Capacité : 4 membres × 4 h = **16 h de travail par séance**.
- La démonstration a lieu à la dernière séance (23/11). *À confirmer avec l'enseignant.*
- Durées reprises des estimations Trello. Le rapport final passe de 6 h à 12 h (3 h par membre), car 6 h était sous-estimé.
- Chaque séance se termine par 30 min de compte-rendu (Sanda) et un point d'équipe.

## Vue d'ensemble

| Sprint | Séance(s) | Objectif du sprint | Terminé quand… |
|---|---|---|---|
| **Sprint 0** | 13/10 | Mise en place du projet | Dépôt, Trello, WBS/PBS et prototype Flask en ligne ✅ |
| **Sprint 1** | 19/10 – 23/10 | **Comptes utilisateurs** fonctionnels | Inscription, connexion et rôles admin / joueur validés ; MCD et structures de données en place |
| **Sprint 2** | 02/11 | **Création de quiz** par l'admin | Création directe et import depuis un fichier texte, avec gestion des erreurs |
| **Sprint 3** | 09/11 | **Passage de quiz** et **historique** | Le joueur passe un quiz, voit son score et la correction, consulte son historique |
| **Sprint 4** | 16/11 – 23/11 | **Tests, rapport et démo** | Version stable sur le dépôt, rapport rendu, démo prête ; bonus si le temps le permet |

Les sprints suivent les priorités du PO (P1 Comptes → P2 Création → P3 Passage → P4 Historique). Comme chaque module est porté par une seule personne, certains membres **commencent le module suivant dès qu'ils sont libres**. Par exemple, Maram démarre l'import de quiz dès le sprint 1. Sans ça, un seul membre aurait 13 à 14 h de travail sur une séance de 4 h.

## Chemin critique (PERT)

**MCD → Structure quiz → Lister les quiz → Questions / réponses → Score et correction → Tests → Rapport + démo**

Il représente 18 h de travail, soit 4,5 séances sur les 6 restantes. Un retard sur l'une de ces tâches retarde toute la fin du projet ; c'est elles qu'il faut surveiller en priorité. La dernière séance (23/11) sert de **marge de sécurité**.

## Détail séance par séance

### Sprint 1 – Comptes utilisateurs

#### Séance 2 – 19/10
| Membre | Travail prévu |
|---|---|
| Omar | Format du fichier d'import + exemples dans `data/` (1 h) ; MCD (3 h) |
| Sanda | Gantt / PERT (2 h) ; Planning des sprints (1 h) ; Compte-rendu (0,5 h) ; début Inscription (0,5 h) |
| Olivier | Corriger la connexion à la base (2 h) ; Table utilisateur avec rôle (2 h) |
| Maram | Import depuis un fichier texte (3 h) ; *1 h libre : aide à Olivier sur la connexion* |

#### Séance 3 – 23/10
| Membre | Travail prévu |
|---|---|
| Omar | Rôles admin / joueur (2 h) ; Lister les quiz (2 h) |
| Sanda | Inscription (2,5 h) ; début Connexion (1 h) ; Compte-rendu (0,5 h) |
| Olivier | Structure quiz / question / réponses (2 h) ; Enregistrer le score (2 h) |
| Maram | Fin de l'import (1 h) ; Erreurs d'import (2 h) ; début Création de quiz (1 h) |

### Sprint 2 – Création de quiz

#### Séance 4 – 02/11
| Membre | Travail prévu |
|---|---|
| Omar | Questions / réponses (4 h) |
| Sanda | Fin de la Connexion (2 h) ; début Page passage du quiz (1,5 h) ; Compte-rendu (0,5 h) |
| Olivier | Afficher l'historique (2 h) ; Page historique (2 h) |
| Maram | Création d'un quiz en saisie directe (3 h) ; début Pages création / import (1 h) |

### Sprint 3 – Passage de quiz et historique

#### Séance 5 – 09/11
| Membre | Travail prévu |
|---|---|
| Omar | Score et correction (3 h) ; Tests (0,5 h) |
| Sanda | Page passage du quiz et score (2,5 h) ; Tests (0,5 h) ; Compte-rendu (0,5 h) |
| Olivier | Tests (0,5 h) ; Minuterie – bonus (1 h) ; *2,5 h libres : aide à Omar sur le score, relecture* |
| Maram | Pages création et import de quiz (3 h) ; Tests (0,5 h) ; Export JSON – bonus (0,5 h) |

### Sprint 4 – Tests, rapport et démo

#### Séance 6 – 16/11
| Membre | Travail prévu |
|---|---|
| Toute l'équipe | Fin des tests (0,5 h chacun) ; **Rapport final + préparation de la démo (3 h chacun)** |
| Sanda | Compte-rendu (0,5 h) |
| Olivier, Maram | Bonus (0,5 h chacun) |

#### Séance 7 – 23/11
| Membre | Travail prévu |
|---|---|
| Toute l'équipe | **Démonstration finale** ; marge pour rattraper un éventuel retard |
| Olivier, Maram | Fin des bonus, uniquement si tout le reste est validé |
| Sanda | Dernier compte-rendu |

## Changements à valider avec l'équipe

Ces réattributions sont nécessaires pour que le planning tienne en 6 séances :

| Carte | Avant | Proposé | Pourquoi |
|---|---|---|---|
| MCD | Olivier | **Omar** | Olivier a déjà la correction de la base et la table utilisateur à faire au sprint 1. Omar est libre en début de projet et le MCD fait partie de l'architecture globale (rôle du PO). |
| Page passage du quiz et score | Omar | **Sanda** | Omar a 13 h de passage de quiz en un seul sprint ; Sanda a de la marge à partir du 02/11. |
| Minuterie (bonus) | Omar | **Olivier** | Olivier est le plus libre en fin de projet. |
| Rapport final + démo | 6 h | **12 h** (3 h par membre) | Estimation plus réaliste. |

Si un de ces changements est refusé, le chemin critique s'allonge et le passage de quiz risque de ne pas être terminé avant les tests.

## Suivi

- À chaque fin de séance : mettre à jour le Trello (cartes déplacées et temps réel), écrire le compte-rendu, comparer l'avancement à ce planning.
- Si une tâche du chemin critique prend du retard, on réaffecte un membre libre dessus dès la séance suivante.
