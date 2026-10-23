// Page d'import : dépôt du fichier, analyse par le serveur, vérification puis enregistrement du quiz
document.addEventListener("DOMContentLoaded", () => {
    // Limites (les mêmes que côté serveur)
    const NB_QUESTIONS_MAX = 20;
    const NB_REPONSES_MIN = 2;
    const NB_REPONSES_MAX = 6;
    // Réglages de chaque mode : extensions acceptées, taille maximale, textes affichés
    const MODES = {
        document: {
            extensions: [".txt", ".pdf"],
            tailleMax: 5_000_000,
            formats: "TXT ou PDF · 5 Mo maximum",
            bouton: "Générer le quiz",
            chargement: "Génération en cours…",
        },
        quiz: {
            extensions: [".txt"],
            tailleMax: 100_000,
            formats: "TXT au format QUIZ: · 100 Ko maximum",
            bouton: "Lire le quiz",
            chargement: "Lecture du fichier…",
        },
    };

    const formAnalyse = document.getElementById("form-analyse");
    const formEnregistrement = document.getElementById("form-enregistrement");
    const etapeFichier = document.getElementById("etape-fichier");
    const etapeVerification = document.getElementById("etape-verification");
    const indicateurFichier = document.getElementById("indicateur-fichier");
    const indicateurVerification = document.getElementById("indicateur-verification");
    const zoneDepot = document.getElementById("zone-depot");
    const champFichier = document.getElementById("fichier-import");
    const fichierChoisi = document.getElementById("fichier-choisi");
    const optionNbQuestions = document.getElementById("option-nb-questions");
    const aideFormat = document.getElementById("aide-format");
    const erreursAnalyse = document.getElementById("erreurs-analyse");
    const erreursEnregistrement = document.getElementById("erreurs-enregistrement");
    const boutonAnalyser = document.getElementById("bouton-analyser");
    const boutonEnregistrer = document.getElementById("bouton-enregistrer");
    const listeQuestions = document.getElementById("liste-questions");
    const boutonAjouterQuestion = document.getElementById("ajouter-question-import");
    const modeleQuestion = document.getElementById("modele-question-import");
    const modeleReponse = document.getElementById("modele-reponse-import");

    // Fichier choisi par l'utilisateur (null tant qu'aucun fichier valide n'est choisi)
    let fichier = null;
    // Compteur pour donner un nom unique au groupe de boutons radio de chaque question
    let compteurQuestions = 0;

    // Renvoie le mode coché : "document" (générer) ou "quiz" (quiz déjà écrit)
    function modeActuel() {
        return formAnalyse.querySelector('input[name="mode"]:checked').value;
    }

    // Affiche une liste d'erreurs dans le bloc donné (ou le cache si la liste est vide)
    function afficherErreurs(bloc, erreurs) {
        bloc.replaceChildren();
        bloc.hidden = erreurs.length === 0;
        if (erreurs.length === 0) return;
        const titre = document.createElement("p");
        titre.className = "importeur-erreurs-titre";
        titre.textContent = erreurs.length === 1 ? "Un problème à corriger :" : `${erreurs.length} problèmes à corriger :`;
        const liste = document.createElement("ul");
        erreurs.forEach((erreur) => {
            const ligne = document.createElement("li");
            ligne.textContent = erreur;
            liste.append(ligne);
        });
        bloc.append(titre, liste);
    }

    // Bouton en attente : désactivé avec une roue qui tourne
    function enChargement(bouton, actif, texte) {
        bouton.disabled = actif;
        bouton.classList.toggle("en-chargement", actif);
        if (texte) bouton.querySelector(".bouton-texte").textContent = texte;
    }

    // Transforme une taille en octets en texte lisible (Ko, Mo)
    function formaterTaille(octets) {
        if (octets < 1000) return `${octets} octets`;
        if (octets < 1_000_000) return `${Math.round(octets / 1000)} Ko`;
        return `${(octets / 1_000_000).toFixed(1).replace(".", ",")} Mo`;
    }

    // Renvoie l'extension d'un nom de fichier en minuscules (".pdf"), ou "" s'il n'en a pas
    function extensionDe(nom) {
        const point = nom.lastIndexOf(".");
        return point === -1 ? "" : nom.slice(point).toLowerCase();
    }

    // ---------- Étape 1 : mode et fichier ----------

    // Met à jour les textes et les options selon le mode choisi
    function appliquerMode() {
        const mode = MODES[modeActuel()];
        document.getElementById("formats-acceptes").textContent = mode.formats;
        champFichier.accept = mode.extensions.join(",");
        boutonAnalyser.querySelector(".bouton-texte").textContent = mode.bouton;
        optionNbQuestions.hidden = modeActuel() !== "document";
        aideFormat.hidden = modeActuel() !== "quiz";
        // Le fichier déjà choisi peut ne plus convenir au nouveau mode
        if (fichier) choisirFichier(fichier);
    }

    // Vérifie le fichier choisi et l'affiche ; renvoie true s'il est accepté
    function choisirFichier(nouveau) {
        const mode = MODES[modeActuel()];
        const extension = extensionDe(nouveau.name);
        let erreur = null;
        if (!mode.extensions.includes(extension)) {
            erreur = modeActuel() === "quiz"
                ? "Un quiz déjà écrit doit être un fichier .txt."
                : "Le document doit être un fichier .txt ou .pdf.";
        } else if (nouveau.size === 0) {
            erreur = "Le fichier est vide.";
        } else if (nouveau.size > mode.tailleMax) {
            erreur = `Le fichier est trop volumineux (${formaterTaille(mode.tailleMax)} maximum).`;
        }

        if (erreur) {
            retirerFichier();
            afficherErreurs(erreursAnalyse, [erreur]);
            return false;
        }

        fichier = nouveau;
        afficherErreurs(erreursAnalyse, []);
        document.getElementById("fichier-extension").textContent = extension.slice(1).toUpperCase();
        document.getElementById("fichier-nom").textContent = nouveau.name;
        document.getElementById("fichier-taille").textContent = formaterTaille(nouveau.size);
        fichierChoisi.hidden = false;
        zoneDepot.hidden = true;
        return true;
    }

    // Oublie le fichier choisi et réaffiche la zone de dépôt
    function retirerFichier() {
        fichier = null;
        // Vide le champ pour pouvoir choisir à nouveau le même fichier
        champFichier.value = "";
        fichierChoisi.hidden = true;
        zoneDepot.hidden = false;
    }

    // Changer de mode met à jour la page
    formAnalyse.querySelectorAll('input[name="mode"]').forEach((radio) => {
        radio.addEventListener("change", appliquerMode);
    });

    // Fichier choisi avec le sélecteur (clic sur la zone de dépôt)
    champFichier.addEventListener("change", () => {
        if (champFichier.files.length) choisirFichier(champFichier.files[0]);
    });

    // Glisser-déposer : on surligne la zone pendant le survol
    // (preventDefault empêche le navigateur d'ouvrir le fichier lui-même)
    ["dragenter", "dragover"].forEach((type) => {
        zoneDepot.addEventListener(type, (evenement) => {
            evenement.preventDefault();
            zoneDepot.classList.add("survol");
        });
    });
    // Le fichier sort de la zone ou est lâché : on enlève le surlignage
    ["dragleave", "drop"].forEach((type) => {
        zoneDepot.addEventListener(type, () => zoneDepot.classList.remove("survol"));
    });
    // Fichier lâché sur la zone : on garde seulement le premier
    zoneDepot.addEventListener("drop", (evenement) => {
        evenement.preventDefault();
        if (evenement.dataTransfer.files.length) choisirFichier(evenement.dataTransfer.files[0]);
    });

    // Bouton « Changer » : retire le fichier et rouvre directement le sélecteur
    document.getElementById("fichier-retirer").addEventListener("click", () => {
        retirerFichier();
        champFichier.click();
    });

    // Envoie le fichier au serveur, qui renvoie les questions (générées ou lues)
    formAnalyse.addEventListener("submit", async (evenement) => {
        evenement.preventDefault();
        if (!fichier) {
            afficherErreurs(erreursAnalyse, ["Choisissez d'abord un fichier."]);
            return;
        }

        const donnees = new FormData();
        donnees.append("fichier", fichier);
        donnees.append("mode", modeActuel());
        donnees.append("nb_questions", document.getElementById("nb-questions").value);

        afficherErreurs(erreursAnalyse, []);
        enChargement(boutonAnalyser, true, MODES[modeActuel()].chargement);
        try {
            const reponse = await fetch("/quiz/importer/analyser", { method: "POST", body: donnees });
            // Réponse vide si le serveur n'a pas renvoyé de JSON (erreur 500 par exemple)
            const resultat = await reponse.json().catch(() => ({}));
            if (!reponse.ok) {
                afficherErreurs(erreursAnalyse, resultat.erreurs || [`Erreur du serveur (code ${reponse.status}). Réessayez.`]);
                return;
            }
            afficherVerification(resultat);
        } catch {
            afficherErreurs(erreursAnalyse, ["Impossible de joindre le serveur. Vérifiez qu'il est bien lancé, puis réessayez."]);
        } finally {
            enChargement(boutonAnalyser, false, MODES[modeActuel()].bouton);
        }
    });

    // ---------- Étape 2 : vérification ----------

    // Passe d'une étape à l'autre (true = vérification, false = fichier) et met à jour l'indicateur 1 / 2
    function changerEtape(verification) {
        etapeFichier.hidden = verification;
        etapeVerification.hidden = !verification;
        indicateurFichier.classList.toggle("actif", !verification);
        indicateurFichier.classList.toggle("fait", verification);
        indicateurVerification.classList.toggle("actif", verification);
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    // Affiche le quiz renvoyé par le serveur pour que l'utilisateur le relise
    function afficherVerification(quiz) {
        document.getElementById("titre-import").value = quiz.titre;
        const nb = quiz.questions.length;
        const origine = quiz.simule ? "générées à partir de" : "lues dans";
        document.getElementById("resume-quiz").textContent =
            `${nb} question${nb > 1 ? "s" : ""} ${origine} « ${fichier.name} ». Corrigez-les si besoin avant d'enregistrer.`;
        document.getElementById("bandeau-simulation").hidden = !quiz.simule;

        // Remplace les questions d'un éventuel import précédent
        listeQuestions.replaceChildren();
        quiz.questions.forEach(ajouterQuestion);
        mettreAJour();
        afficherErreurs(erreursEnregistrement, []);
        changerEtape(true);
        // Place le focus sur le titre de l'étape (utile au clavier et aux lecteurs d'écran)
        document.getElementById("titre-verification").focus();
    }

    // Ajoute une carte de question (vide si aucune question n'est donnée)
    function ajouterQuestion(question = { texte: "", choix: ["", ""], reponse: null }) {
        const carte = modeleQuestion.content.firstElementChild.cloneNode(true);
        // Nom commun aux boutons radio de cette question : une seule bonne réponse cochable
        carte.dataset.groupe = `bonne-reponse-${compteurQuestions++}`;
        carte.querySelector(".question-import-texte").value = question.texte;
        question.choix.forEach((choix, indice) => ajouterReponse(carte, choix, indice === question.reponse));
        listeQuestions.append(carte);
        return carte;
    }

    // Ajoute une ligne de réponse à une question (cochée si c'est la bonne réponse)
    function ajouterReponse(carte, texte = "", correcte = false) {
        const ligne = modeleReponse.content.firstElementChild.cloneNode(true);
        const radio = ligne.querySelector(".reponse-import-correcte");
        radio.name = carte.dataset.groupe;
        radio.checked = correcte;
        ligne.querySelector(".reponse-import-texte").value = texte;
        carte.querySelector(".reponses-import").append(ligne);
    }

    // Renumérote les questions et les réponses, et applique les limites (boutons cachés ou désactivés)
    function mettreAJour() {
        const cartes = listeQuestions.querySelectorAll(".question-import");
        cartes.forEach((carte, indice) => {
            const numero = indice + 1;
            carte.querySelector(".question-import-numero").textContent = `Question ${numero}`;
            carte.querySelector(".question-import-texte").setAttribute("aria-label", `Énoncé de la question ${numero}`);
            carte.querySelector(".question-import-supprimer").hidden = cartes.length <= 1;
            carte.querySelector(".question-import-supprimer").setAttribute("aria-label", `Supprimer la question ${numero}`);

            const lignes = carte.querySelectorAll(".reponse-import");
            lignes.forEach((ligne, indiceReponse) => {
                // 0 → A, 1 → B, 2 → C...
                const lettre = String.fromCharCode(65 + indiceReponse);
                ligne.querySelector(".reponse-import-texte").placeholder = `Réponse ${lettre}`;
                ligne.querySelector(".reponse-import-texte").setAttribute("aria-label", `Question ${numero}, réponse ${lettre}`);
                ligne.querySelector(".reponse-import-correcte").setAttribute("aria-label", `Réponse ${lettre} est la bonne réponse`);
                ligne.querySelector(".reponse-import-supprimer").hidden = lignes.length <= NB_REPONSES_MIN;
                ligne.querySelector(".reponse-import-supprimer").setAttribute("aria-label", `Supprimer la réponse ${lettre}`);
                ligne.classList.toggle("correcte", ligne.querySelector(".reponse-import-correcte").checked);
            });
            carte.querySelector(".ajouter-reponse-import").hidden = lignes.length >= NB_REPONSES_MAX;
        });
        boutonAjouterQuestion.hidden = cartes.length >= NB_QUESTIONS_MAX;
    }

    // Un seul écouteur pour tous les boutons des questions, y compris celles ajoutées plus tard
    listeQuestions.addEventListener("click", (evenement) => {
        const carte = evenement.target.closest(".question-import");
        if (!carte) return;

        // Bouton « Supprimer » de la question
        if (evenement.target.closest(".question-import-supprimer")) {
            carte.remove();
        // Bouton « + Ajouter une réponse » : on place le curseur dans la nouvelle réponse
        } else if (evenement.target.closest(".ajouter-reponse-import")) {
            ajouterReponse(carte);
            carte.querySelector(".reponse-import:last-child .reponse-import-texte").focus();
        // Bouton × d'une réponse
        } else if (evenement.target.closest(".reponse-import-supprimer")) {
            evenement.target.closest(".reponse-import").remove();
        // Clic ailleurs dans la carte : rien à faire
        } else {
            return;
        }
        mettreAJour();
    });

    // Cocher une bonne réponse la met en vert
    listeQuestions.addEventListener("change", (evenement) => {
        if (evenement.target.matches(".reponse-import-correcte")) mettreAJour();
    });

    // Bouton « + Ajouter une question » : ajoute une question vide et place le curseur dedans
    boutonAjouterQuestion.addEventListener("click", () => {
        const carte = ajouterQuestion();
        mettreAJour();
        carte.querySelector(".question-import-texte").focus();
    });

    // Bouton « Retour » : revient à l'étape 1 sans perdre le fichier choisi
    document.getElementById("bouton-retour").addEventListener("click", () => changerEtape(false));

    // Lit le quiz tel qu'il est affiché (avec les corrections de l'utilisateur)
    function lireQuiz() {
        return {
            titre: document.getElementById("titre-import").value.trim(),
            visibilite: document.getElementById("visibilite-import").value,
            duree: Number(document.getElementById("duree-import").value),
            questions: Array.from(listeQuestions.querySelectorAll(".question-import"), (carte) => {
                const lignes = Array.from(carte.querySelectorAll(".reponse-import"));
                const bonne = lignes.findIndex((ligne) => ligne.querySelector(".reponse-import-correcte").checked);
                return {
                    texte: carte.querySelector(".question-import-texte").value.trim(),
                    choix: lignes.map((ligne) => ligne.querySelector(".reponse-import-texte").value.trim()),
                    reponse: bonne === -1 ? null : bonne,
                };
            }),
        };
    }

    // Vérifie le quiz avant l'envoi et signale les questions incomplètes
    function verifierQuiz(quiz) {
        const erreurs = [];
        if (!quiz.titre) erreurs.push("Donnez un titre au quiz.");
        if (!Number.isInteger(quiz.duree) || quiz.duree < 10 || quiz.duree > 3600) {
            erreurs.push("Le minuteur doit être compris entre 10 et 3600 secondes.");
        }
        const cartes = listeQuestions.querySelectorAll(".question-import");
        quiz.questions.forEach((question, indice) => {
            const problemes = [];
            if (!question.texte) problemes.push("l'énoncé est vide");
            if (question.choix.some((choix) => !choix)) problemes.push("une réponse est vide");
            if (question.reponse === null) problemes.push("aucune bonne réponse n'est cochée");
            cartes[indice].classList.toggle("a-corriger", problemes.length > 0);
            if (problemes.length) erreurs.push(`Question ${indice + 1} : ${problemes.join(", ")}.`);
        });
        return erreurs;
    }

    // Envoie le quiz vérifié au serveur, qui l'enregistre puis renvoie vers l'accueil
    formEnregistrement.addEventListener("submit", async (evenement) => {
        evenement.preventDefault();
        const quiz = lireQuiz();
        const erreurs = verifierQuiz(quiz);
        afficherErreurs(erreursEnregistrement, erreurs);
        if (erreurs.length) {
            const premiere = listeQuestions.querySelector(".a-corriger");
            (premiere || document.getElementById("titre-import")).scrollIntoView({ behavior: "smooth", block: "center" });
            return;
        }

        enChargement(boutonEnregistrer, true, "Enregistrement…");
        try {
            const reponse = await fetch("/quiz/importer/enregistrer", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(quiz),
            });
            // Réponse vide si le serveur n'a pas renvoyé de JSON (erreur 500 par exemple)
            const resultat = await reponse.json().catch(() => ({}));
            if (!reponse.ok) {
                afficherErreurs(erreursEnregistrement, resultat.erreurs || [`Erreur du serveur (code ${reponse.status}). Réessayez.`]);
                return;
            }
            // Quiz enregistré : le serveur indique où aller (l'accueil, avec un message de succès)
            window.location.href = resultat.redirection;
        } catch {
            // fetch échoue seulement si le serveur ne répond pas du tout
            afficherErreurs(erreursEnregistrement, ["Impossible de joindre le serveur. Vérifiez qu'il est bien lancé, puis réessayez."]);
        } finally {
            enChargement(boutonEnregistrer, false, "Enregistrer le quiz");
        }
    });

    // Au chargement : affiche les textes du mode coché par défaut (« Générer à partir d'un document »)
    appliquerMode();
});
