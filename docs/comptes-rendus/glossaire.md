# Glossaire – QuizApp (PROJ531, groupe 4)

Les termes techniques et de gestion de projet utilisés dans le dépôt, les comptes-rendus et le rapport.

| Terme | Définition |
|---|---|
| **API** | Interface qui permet à un programme d'utiliser un service extérieur. QuizApp utilise l'API de Groq pour générer des quiz. |
| **Association** | Dans un MCD, lien entre deux entités (par exemple, un utilisateur CRÉE un quiz). |
| **Backlog** | Liste priorisée des fonctionnalités à réaliser, sous forme de user stories ; dans notre projet, les cartes Trello. |
| **Branche** | Copie de travail du code dans Git, qui permet de développer une tâche sans toucher à la version principale. |
| **Cardinalité** | Dans un MCD, nombre minimum et maximum de fois qu'une entité participe à une association (par exemple 1,20 : de 1 à 20 questions par quiz). |
| **Chemin critique** | Suite de tâches du PERT sans marge : le moindre retard sur l'une d'elles retarde tout le projet. |
| **Clé étrangère** | Colonne d'une table qui fait référence à une ligne d'une autre table et garantit la cohérence des données. |
| **Clé primaire** | Colonne qui identifie de façon unique chaque ligne d'une table (par exemple id_quizz). |
| **Code de partage** | Code de 6 caractères, unique, qui donne accès à un quiz privé. |
| **Commit** | Enregistrement d'un ensemble de modifications dans l'historique Git, avec un message et une date. |
| **Compte-rendu de séance** | Document déposé sur GitHub après chaque séance : travail réalisé, temps estimés et réels, problèmes, décisions, tâches suivantes. |
| **Critère d'acceptation** | Condition vérifiable qu'une fonctionnalité doit remplir pour être considérée comme terminée. |
| **CSRF** | Attaque où un site extérieur fait envoyer un formulaire à l'insu de l'utilisateur connecté ; on s'en protège avec un jeton secret dans chaque formulaire. |
| **Définition de « terminé »** | Règle commune de l'équipe : une carte est terminée quand sa Pull Request est testée et fusionnée, et ses critères d'acceptation vérifiés. |
| **Dépôt (repository)** | Espace GitHub qui contient le code, la documentation et tout leur historique. |
| **Discord** | Messagerie utilisée par l'équipe entre les séances. |
| **draw.io** | Outil gratuit de dessin de diagrammes, utilisé pour le WBS, le PBS, le PERT et le MCD. |
| **Entité** | Dans un MCD, objet dont on garde les informations (utilisateur, quiz, question, réponse, tentative, document). |
| **Flask** | Bibliothèque Python pour créer des applications web : elle associe chaque adresse (route) à une fonction. |
| **Fusion (merge)** | Intégration des modifications d'une branche dans main, une fois la Pull Request acceptée. |
| **Gabarit (template)** | Fichier HTML avec des zones remplies par Flask (avec Jinja2) au moment d'afficher la page. |
| **Gantt** | Diagramme qui place les tâches sur un calendrier, par membre, et montre l'avance ou le retard. |
| **Gel du code** | Moment à partir duquel on ne fusionne plus que des corrections de bugs (pour nous, le 16/11 à 17h30). |
| **Git / GitHub** | Git enregistre l'historique du code ; GitHub héberge le dépôt en ligne et gère les Pull Requests. |
| **Groq** | Service en ligne d'intelligence artificielle utilisé par QuizApp pour générer un quiz à partir d'un cours. |
| **Hachage** | Transformation irréversible d'un mot de passe, pour ne jamais le stocker en clair dans la base. |
| **Import** | Création d'un quiz à partir d'un fichier texte écrit au format QUIZ: / Q: / + / -. |
| **Incrément** | Version de l'application obtenue à la fin d'un sprint ; pour nous, la branche main. |
| **Jalon** | Date ou étape importante du projet, utilisée pour comparer le prévu et le réel. |
| **Jinja2** | Langage de gabarits utilisé par Flask pour produire les pages HTML. |
| **JSON** | Format de texte structuré pour échanger des données entre programmes. |
| **main** | Branche principale du dépôt, qui doit toujours contenir une version qui fonctionne. |
| **Marge** | Dans le PERT, retard qu'une tâche peut prendre sans retarder la fin du projet. |
| **MCD** | Modèle conceptuel de données : schéma des entités, de leurs attributs et de leurs associations. |
| **Mêlée quotidienne** | Court point d'avancement de l'équipe en Scrum ; chez nous, remplacé par Discord et un point en séance. |
| **MLD** | Modèle logique de données : traduction du MCD en tables, avec clés primaires et clés étrangères. |
| **Minuteur** | Compte à rebours affiché pendant un quiz ; les réponses sont envoyées automatiquement à la fin. |
| **PBS** | Product Breakdown Structure : décomposition du produit livré en blocs. |
| **PERT** | Réseau qui montre l'enchaînement des tâches, leurs dépendances, leurs marges et le chemin critique. |
| **Plan B** | Génération simulée de questions, utilisée quand le service Groq n'est pas disponible (pas d'internet, pas de clé…). |
| **Product Owner (PO)** | Membre responsable de la vision du produit, du backlog, des décisions produit et de la validation. |
| **Pull Request (PR)** | Demande de fusion d'une branche dans main, relue et testée avant d'être acceptée. |
| **Quiz privé / public** | Quiz visible par tous (public) ou accessible uniquement avec un code de partage (privé). |
| **README** | Fichier de présentation du dépôt : objectif, fonctionnalités, installation, utilisation, tests. |
| **Rétrospective** | Moment où l'équipe analyse ce qui a marché ou non et fixe de nouvelles règles ; chez nous, les bilans et comptes-rendus. |
| **Revue de sprint** | Vérification de ce qui a été livré à la fin d'un sprint ; chez nous, le test de main par le PO. |
| **Route** | Adresse de l'application (par exemple /historique) associée à une fonction Flask. |
| **Scrum** | Méthode agile qui découpe le projet en sprints courts, avec un backlog priorisé. |
| **Scrum Master** | Membre qui organise et suit le travail de l'équipe (planning, Trello, comptes-rendus) sans développer. |
| **Session** | Mémoire, côté serveur, de l'utilisateur connecté, signée avec la clé secrète SECRET_KEY. |
| **Sprint** | Période courte de travail avec un objectif précis (ici, une à deux séances). |
| **SQLite** | Base de données relationnelle stockée dans un seul fichier, sans serveur à installer. |
| **Temps estimé / temps réel** | Durée prévue pour une tâche avant de la commencer, et durée réellement passée, notées dans Trello. |
| **Tentative** | Un passage d'un quiz par un utilisateur, avec son score et sa date ; c'est ce que montre l'historique. |
| **Test automatique** | Petit programme qui vérifie qu'une fonction donne le bon résultat ; le projet en compte 34 (unittest). |
| **Trello** | Tableau en ligne de cartes et de colonnes (Backlog, En cours, En revue, Terminé), utilisé pour suivre les tâches. |
| **User story** | Besoin formulé du point de vue de l'utilisateur : « En tant que…, je veux…, afin de… ». |
| **Variable d'environnement** | Réglage donné à l'application en dehors du code (clé Groq, clé secrète), pour ne jamais publier de secret sur GitHub. |
| **WBS** | Work Breakdown Structure : décomposition du travail à réaliser en lots et en tâches. |
