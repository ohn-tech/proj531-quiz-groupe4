// Formulaire de création de quiz : ajout/suppression de questions et de réponses, validation, puis envoi au serveur
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-creation-quiz");
    const questions = document.getElementById("questions-quiz");
    const questionTemplate = document.getElementById("modele-question");
    const answerTemplate = document.getElementById("modele-reponse");
    const addQuestionButton = document.getElementById("ajouter-question");
    const status = document.getElementById("quiz-form-status");

    // Pas de formulaire de création sur cette page (utilisateur non connecté) : rien à faire
    if (!form || !questions || !questionTemplate || !answerTemplate || !addQuestionButton) return;

    // Renumérote les réponses d'une question et met à jour leurs noms de champs et leur style
    function updateAnswers(questionCard, questionIndex) {
        const answerRows = questionCard.querySelectorAll(".answer-option");
        const hasCorrectAnswer = questionCard.querySelector("[data-correct-answer]:checked") !== null;

        answerRows.forEach((row, answerIndex) => {
            const radio = row.querySelector("[data-correct-answer]");
            const answer = row.querySelector("[data-answer]");
            const removeButton = row.querySelector(".supprimer-reponse");

            // Boutons radio d'une même question : même nom, donc une seule bonne réponse possible.
            // La valeur envoyée est le numéro de la bonne réponse (0, 1, 2...)
            radio.name = `questions[${questionIndex}][correct]`;
            radio.value = String(answerIndex);
            radio.setAttribute("aria-label", `Marquer la réponse ${answerIndex + 1} comme correcte`);
            // Noms au format questions[i][answers][j][...] pour garder l'ordre à l'envoi
            answer.name = `questions[${questionIndex}][answers][${answerIndex}][answer]`;
            answer.placeholder = `Réponse ${answerIndex + 1}`;
            answer.setAttribute("aria-label", `Réponse ${answerIndex + 1}`);
            // Une question garde au moins 2 réponses : on cache alors le bouton ×
            removeButton.hidden = answerRows.length <= 2;
            removeButton.setAttribute("aria-label", `Supprimer la réponse ${answerIndex + 1}`);

            // Colore en vert la bonne réponse, et en rouge les autres dès qu'elle est choisie
            row.classList.toggle("is-correct", radio.checked);
            row.classList.toggle("is-incorrect", hasCorrectAnswer && !radio.checked);
        });

        // 6 réponses maximum par question
        questionCard.querySelector(".ajouter-reponse").disabled = answerRows.length >= 6;
    }

    // Renumérote toutes les questions après un ajout ou une suppression
    function updateQuestions() {
        const cards = questions.querySelectorAll(".question-a-creer");
        cards.forEach((card, questionIndex) => {
            card.querySelector("legend").textContent = `Question ${questionIndex + 1}`;
            card.querySelector('[data-field="question"]').name = `questions[${questionIndex}][question]`;
            card.querySelector('[data-field="award"]').name = `questions[${questionIndex}][award]`;
            // Impossible de supprimer la dernière question restante
            card.querySelector(".supprimer-question").hidden = cards.length <= 1;
            updateAnswers(card, questionIndex);
        });
        // 20 questions maximum par quiz
        addQuestionButton.disabled = cards.length >= 20;
    }

    // Ajoute une nouvelle question à partir du modèle <template id="modele-question">
    addQuestionButton.addEventListener("click", () => {
        if (questions.querySelectorAll(".question-a-creer").length >= 20) return;
        questions.append(questionTemplate.content.cloneNode(true));
        updateQuestions();
    });

    // Un seul écouteur pour tous les boutons des questions, y compris celles ajoutées plus tard
    questions.addEventListener("click", (event) => {
        // Bouton "Ajouter une réponse"
        const addAnswerButton = event.target.closest(".ajouter-reponse");
        if (addAnswerButton) {
            const card = addAnswerButton.closest(".question-a-creer");
            if (card.querySelectorAll(".answer-option").length < 6) {
                card.querySelector(".answers-for-question").append(answerTemplate.content.cloneNode(true));
                updateQuestions();
            }
            return;
        }

        // Bouton × qui supprime une réponse
        const removeAnswerButton = event.target.closest(".supprimer-reponse");
        if (removeAnswerButton) {
            const card = removeAnswerButton.closest(".question-a-creer");
            if (card.querySelectorAll(".answer-option").length > 2) {
                removeAnswerButton.closest(".answer-option").remove();
                updateQuestions();
            }
            return;
        }

        // Bouton "Supprimer cette question"
        const removeQuestionButton = event.target.closest(".supprimer-question");
        if (removeQuestionButton && questions.querySelectorAll(".question-a-creer").length > 1) {
            removeQuestionButton.closest(".question-a-creer").remove();
            updateQuestions();
        }
    });

    // Choisir la bonne réponse met à jour les couleurs
    questions.addEventListener("change", (event) => {
        if (event.target.matches("[data-correct-answer]")) {
            updateQuestions();
        }
    });

    // Envoi du formulaire : s'il est valide, le navigateur l'envoie à la route /quiz/creer
    form.addEventListener("submit", (event) => {
        // Affiche les messages du navigateur pour les champs obligatoires vides
        if (!form.reportValidity()) {
            event.preventDefault();
            return;
        }

        // Chaque question doit avoir sa bonne réponse cochée (une seule, grâce aux boutons radio)
        const unansweredQuestion = Array.from(questions.querySelectorAll(".question-a-creer"))
            .find((card) => !card.querySelector("[data-correct-answer]:checked"));
        if (unansweredQuestion) {
            event.preventDefault();
            status.textContent = "Choisissez la bonne réponse de chaque question.";
            unansweredQuestion.querySelector("[data-correct-answer]").focus();
        }
    });

    // Met en place la numérotation de la première question au chargement
    updateQuestions();
});
