// Comportement de la barre de navigation
document.addEventListener("DOMContentLoaded", () => {
    const bouton = document.getElementById("nav-bouton");
    const liens = document.getElementById("nav-liens");
    const menuUtilisateur = document.getElementById("menu-utilisateur");

    // Petit écran : le bouton ☰ affiche ou cache les liens
    bouton.addEventListener("click", () => {
        const ouvert = liens.classList.toggle("ouvert");
        bouton.setAttribute("aria-expanded", ouvert);
    });

    // Ferme le menu utilisateur quand on clique ailleurs sur la page
    document.addEventListener("click", (evenement) => {
        if (!menuUtilisateur.contains(evenement.target)) {
            menuUtilisateur.removeAttribute("open");
        }
    });
});
