/**
 * Mécanisme de fonctionnement hors-ligne poste↔serveur (chapitre 3.8, 4.5).
 *
 * 4 éléments requis par le mémoire :
 *   1. Cache local restreint (catalogue produits, nomenclature actes,
 *      diagnostics fréquents, dossiers de la file d'attente du jour
 *      uniquement — jamais la base entière).
 *   2. File d'attente d'opérations : chaque écriture reçoit un UUID
 *      généré côté client, enregistrée localement, confirmation immédiate.
 *   3. Rejeu idempotent au retour réseau, l'UUID empêche tout doublon.
 *   4. Résolution de conflits différenciée par type de donnée (Tableau 13).
 *
 * DECISIONS.md #9 : la "file d'attente du jour" est purgée à minuit local ;
 * elle ne contient que les dossiers avec passage/RDV du jour courant.
 */

const SIHL_DB_NOM = "sihl-hors-ligne";
const SIHL_DB_VERSION = 1;
const MAGASIN_FILE_OPERATIONS = "file_operations";
const MAGASIN_CACHE_JOUR = "cache_jour";

/** Politique de résolution de conflit par type de donnée (Tableau 13). */
const POLITIQUE_CONFLIT = {
    ECRITURE_CLINIQUE: "AUCUN_CONFLIT_NOUVEL_ENREGISTREMENT",
    IDENTITE_PATIENT: "DERNIERE_ECRITURE_GAGNANTE",
    STOCK_CAISSE: "SERIALISATION_STRICTE_SERVEUR",
};

function ouvrirBaseLocale() {
    return new Promise((resolve, reject) => {
        const requete = indexedDB.open(SIHL_DB_NOM, SIHL_DB_VERSION);
        requete.onupgradeneeded = () => {
            const db = requete.result;
            if (!db.objectStoreNames.contains(MAGASIN_FILE_OPERATIONS)) {
                db.createObjectStore(MAGASIN_FILE_OPERATIONS, { keyPath: "uuid" });
            }
            if (!db.objectStoreNames.contains(MAGASIN_CACHE_JOUR)) {
                db.createObjectStore(MAGASIN_CACHE_JOUR, { keyPath: "cle" });
            }
        };
        requete.onsuccess = () => resolve(requete.result);
        requete.onerror = () => reject(requete.error);
    });
}

function genererUUID() {
    if (crypto.randomUUID) return crypto.randomUUID();
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        const v = c === "x" ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
}

/**
 * File d'attente d'opérations persistante. Chaque écriture confirmée à
 * l'utilisateur immédiatement, rejouée dès le retour réseau.
 */
class FileOperations {
    constructor() {
        this.enAttente = 0;
        this.ecouteurs = [];
    }

    surChangement(callback) {
        this.ecouteurs.push(callback);
    }

    _notifier() {
        this.ecouteurs.forEach((cb) => cb(this.enAttente));
    }

    async ajouter(operation) {
        const db = await ouvrirBaseLocale();
        const uuid = genererUUID();
        const enregistrement = {
            uuid,
            operation, // { methode, url, corps, type_donnee }
            cree_le: Date.now(),
            tentatives: 0,
        };
        await new Promise((resolve, reject) => {
            const tx = db.transaction(MAGASIN_FILE_OPERATIONS, "readwrite");
            tx.objectStore(MAGASIN_FILE_OPERATIONS).put(enregistrement);
            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });
        await this._rafraichirCompteur();
        return uuid;
    }

    async _rafraichirCompteur() {
        const db = await ouvrirBaseLocale();
        const liste = await new Promise((resolve, reject) => {
            const tx = db.transaction(MAGASIN_FILE_OPERATIONS, "readonly");
            const requete = tx.objectStore(MAGASIN_FILE_OPERATIONS).getAll();
            requete.onsuccess = () => resolve(requete.result);
            requete.onerror = () => reject(requete.error);
        });
        this.enAttente = liste.length;
        this._notifier();
        return liste;
    }

    /** Rejeu idempotent : l'UUID de chaque opération empêche tout doublon serveur. */
    async rejouer() {
        const db = await ouvrirBaseLocale();
        const enAttente = await this._rafraichirCompteur();
        enAttente.sort((a, b) => a.cree_le - b.cree_le);

        for (const enregistrement of enAttente) {
            try {
                const reponse = await fetch(enregistrement.operation.url, {
                    method: enregistrement.operation.methode,
                    headers: {
                        "Content-Type": "application/json",
                        "X-Idempotency-Key": enregistrement.uuid,
                    },
                    body: JSON.stringify(enregistrement.operation.corps || {}),
                });
                if (reponse.ok || reponse.status === 409) {
                    // 409 = déjà rejouée côté serveur grâce à l'UUID : on purge quand même.
                    await this._supprimer(enregistrement.uuid);
                } else {
                    enregistrement.tentatives += 1;
                    await this._mettreAJour(enregistrement);
                }
            } catch (erreur) {
                // Toujours hors-ligne : on réessaiera au prochain cycle.
                break;
            }
        }
        await this._rafraichirCompteur();
    }

    async _supprimer(uuid) {
        const db = await ouvrirBaseLocale();
        return new Promise((resolve, reject) => {
            const tx = db.transaction(MAGASIN_FILE_OPERATIONS, "readwrite");
            tx.objectStore(MAGASIN_FILE_OPERATIONS).delete(uuid);
            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });
    }

    async _mettreAJour(enregistrement) {
        const db = await ouvrirBaseLocale();
        return new Promise((resolve, reject) => {
            const tx = db.transaction(MAGASIN_FILE_OPERATIONS, "readwrite");
            tx.objectStore(MAGASIN_FILE_OPERATIONS).put(enregistrement);
            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });
    }
}

/** Cache local restreint : uniquement la file d'attente du jour (DECISIONS.md #9). */
class CacheJour {
    async enregistrer(cle, valeur) {
        const db = await ouvrirBaseLocale();
        return new Promise((resolve, reject) => {
            const tx = db.transaction(MAGASIN_CACHE_JOUR, "readwrite");
            tx.objectStore(MAGASIN_CACHE_JOUR).put({ cle, valeur, date: this._aujourdhui() });
            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });
    }

    async lire(cle) {
        const db = await ouvrirBaseLocale();
        return new Promise((resolve, reject) => {
            const tx = db.transaction(MAGASIN_CACHE_JOUR, "readonly");
            const requete = tx.objectStore(MAGASIN_CACHE_JOUR).get(cle);
            requete.onsuccess = () => resolve(requete.result ? requete.result.valeur : null);
            requete.onerror = () => reject(requete.error);
        });
    }

    /** Purge quotidienne : ne conserve que les entrées du jour courant. */
    async purgerVeille() {
        const db = await ouvrirBaseLocale();
        const aujourdhui = this._aujourdhui();
        return new Promise((resolve, reject) => {
            const tx = db.transaction(MAGASIN_CACHE_JOUR, "readwrite");
            const magasin = tx.objectStore(MAGASIN_CACHE_JOUR);
            const requete = magasin.getAll();
            requete.onsuccess = () => {
                requete.result
                    .filter((entree) => entree.date !== aujourdhui)
                    .forEach((entree) => magasin.delete(entree.cle));
            };
            tx.oncomplete = resolve;
            tx.onerror = () => reject(tx.error);
        });
    }

    _aujourdhui() {
        return new Date().toISOString().slice(0, 10);
    }
}

const fileOperations = new FileOperations();
const cacheJour = new CacheJour();

/** Surveillance de la liaison poste↔serveur : rejeu automatique au retour réseau. */
window.addEventListener("online", () => fileOperations.rejouer());
setInterval(() => {
    if (navigator.onLine) fileOperations.rejouer();
}, 30_000);
cacheJour.purgerVeille();

window.SIHLSync = { fileOperations, cacheJour, POLITIQUE_CONFLIT, genererUUID };
