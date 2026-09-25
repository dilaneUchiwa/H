/**
 * Client HTTP pour l'API DRF : gère le cookie CSRF (SessionAuthentication),
 * le JSON, et la file d'attente hors-ligne (chapitre 3.8) pour les écritures.
 */

function lireCookie(nom) {
    const valeur = document.cookie.match("(^|;)\\s*" + nom + "\\s*=\\s*([^;]+)");
    return valeur ? decodeURIComponent(valeur.pop()) : "";
}

async function api(chemin, { methode = "GET", corps = null } = {}) {
    const options = {
        method: methode,
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
    };
    if (methode !== "GET") {
        options.headers["X-CSRFToken"] = lireCookie("csrftoken");
    }
    if (corps !== null) {
        options.body = JSON.stringify(corps);
    }

    const reponse = await fetch(`/api${chemin}`, options);

    if (reponse.status === 204) return null;

    let donnees = null;
    try {
        donnees = await reponse.json();
    } catch (erreur) {
        donnees = null;
    }

    if (!reponse.ok) {
        const erreur = new Error(donnees && donnees.detail ? donnees.detail : `Erreur ${reponse.status}`);
        erreur.status = reponse.status;
        erreur.donnees = donnees;
        throw erreur;
    }
    return donnees;
}

// Liste paginée DRF : renvoie toujours { count, results } même sans pagination.
async function apiListe(chemin, params = {}) {
    const qs = new URLSearchParams(params).toString();
    const donnees = await api(chemin + (qs ? `?${qs}` : ""));
    if (donnees && Array.isArray(donnees.results)) return donnees;
    return { count: Array.isArray(donnees) ? donnees.length : 0, results: donnees || [] };
}

window.SIHLApi = { api, apiListe, lireCookie };
