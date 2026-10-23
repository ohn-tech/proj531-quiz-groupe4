// Formulaire de création de quiz : ajout/suppression de questions et de réponses, puis validation
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
        const hasCorrectAnswers = questionCard.querySelector("[data-correct-answer]:checked") !== null;

        answerRows.forEach((row, answerIndex) => {
            const checkbox = row.querySelector("[data-correct-answer]");
            const answer = row.querySelector("[data-answer]");
            const removeButton = row.querySelector(".supprimer-reponse");

            // Noms au format questions[i][answers][j][...] pour garder l'ordre à l'envoi
            checkbox.name = `questions[${questionIndex}][answers][${answerIndex}][is_correct]`;
            checkbox.value = checkbox.checked ? "1" : "0";
            checkbox.setAttribute("aria-label", `Marquer la réponse ${answerIndex + 1} comme correcte`);
            answer.name = `questions[${questionIndex}][answers][${answerIndex}][answer]`;
            answer.placeholder = `Réponse ${answerIndex + 1}`;
            answer.setAttribute("aria-label", `Réponse ${answerIndex + 1}`);
            // Une question garde au moins 2 réponses : on cache alors le bouton ×
            removeButton.hidden = answerRows.length <= 2;
            removeButton.setAttribute("aria-label", `Supprimer la réponse ${answerIndex + 1}`);

            // Colore en vert les bonnes réponses, et en rouge les autres dès qu'une est cochée
            row.classList.toggle("is-correct", checkbox.checked);
            row.classList.toggle("is-incorrect", hasCorrectAnswers && !checkbox.checked);
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

    // Cocher ou décocher une bonne réponse met à jour les couleurs
    questions.addEventListener("change", (event) => {
        if (event.target.matches("[data-correct-answer]")) {
            updateQuestions();
        }
    });

    // Envoi du formulaire : vérifie les champs puis prépare les données du quiz
    form.addEventListener("submit", (event) => {
        // Pas d'envoi au serveur pour l'instant (backend pas encore relié)
        event.preventDefault();
        // Affiche les messages du navigateur pour les champs obligatoires vides
        if (!form.reportValidity()) return;

        // Chaque question doit avoir au moins une bonne réponse cochée
        const unansweredQuestion = Array.from(questions.querySelectorAll(".question-a-creer"))
            .find((card) => !card.querySelector("[data-correct-answer]:checked"));
        if (unansweredQuestion) {
            status.textContent = "Sélectionnez au moins une bonne réponse pour chaque question.";
            unansweredQuestion.querySelector("[data-correct-answer]").focus();
            return;
        }

        // Construit l'objet quiz au format des tables quizz, questions et answers
        const data = new FormData(form);
        const quiz = {
            title: data.get("title").trim(),
            description: data.get("description").trim(),
            subject: data.get("subject").trim(),
            is_public: Number(data.get("is_public")),
            difficulty: data.get("difficulty"),
            code: data.get("code").trim(),
            link: data.get("link").trim(),
            timer: Number(data.get("timer")),
            questions: Array.from(questions.querySelectorAll(".question-a-creer"), (card) => {
                return {
                    question: card.querySelector('[data-field="question"]').value.trim(),
                    award: Number(card.querySelector('[data-field="award"]').value),
                    answers: Array.from(card.querySelectorAll(".answer-option"), (row) => ({
                        answer: row.querySelector("[data-answer]").value.trim(),
                        is_correct: row.querySelector("[data-correct-answer]").checked,
                    })),
                };
            }),
        };

        // Événement "quiz:ready" que le futur code d'enregistrement pourra écouter
        form.dispatchEvent(new CustomEvent("quiz:ready", { bubbles: true, detail: quiz }));
        status.textContent = "Formulaire valide et prêt pour l'intégration backend. Aucune donnée n'a encore été enregistrée.";
    });

    // Met en place la numérotation de la première question au chargement
    updateQuestions();
});
