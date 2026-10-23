// Minuteur du quiz : compte à rebours, puis envoi automatique des réponses à 0
document.addEventListener("DOMContentLoaded", () => {
    const minuteur = document.getElementById("minuteur");
    // Pas de minuteur sur cette page : rien à faire
    if (!minuteur) return;

    const affichage = document.getElementById("minuteur-temps");
    const barre = document.getElementById("barre-temps");
    const formulaire = document.getElementById("form-quiz");
    const champTempsEcoule = document.getElementById("temps-ecoule");

    // Durée en secondes, définie par le quiz (attribut data-duree)
    const duree = parseInt(minuteur.dataset.duree, 10);
    // Heure de fin : on se base sur l'horloge pour ne pas dériver si l'onglet est en arrière-plan
    const fin = Date.now() + duree * 1000;
    let termine = false;
    let intervalle = null;

    // Transforme un nombre de secondes en "mm:ss"
    function formater(secondes) {
        const minutes = Math.floor(secondes / 60);
        const reste = secondes % 60;
        return String(minutes).padStart(2, "0") + ":" + String(reste).padStart(2, "0");
    }

    // Met à jour l'affichage et envoie le formulaire quand le temps est écoulé
    function miseAJour() {
        const restant = Math.max(0, Math.ceil((fin - Date.now()) / 1000));
        affichage.textContent = formater(restant);
        barre.style.width = (restant / duree) * 100 + "%";
        // Passe en rouge pendant les 10 dernières secondes
        minuteur.classList.toggle("urgent", restant <= 10);
        barre.classList.toggle("urgent", restant <= 10);

        if (restant === 0 && !termine) {
            termine = true;
            clearInterval(intervalle);
            champTempsEcoule.value = "1";
            formulaire.submit();
        }
    }

    // L'utilisateur valide lui-même : on arrête le minuteur
    formulaire.addEventListener("submit", () => {
        termine = true;
        clearInterval(intervalle);
    });

    miseAJour();
    intervalle = setInterval(miseAJour, 250);
});
