/**
 * Coquille PWA minimale (chapitre 3.2, 4.1). Vue 3 sans étape de
 * compilation : ce fichier est chargé tel quel par le navigateur.
 *
 * Bandeau d'état permanent (règle d'ergonomie n°5, chapitre 5.4) : indique
 * l'état de la liaison et le nombre d'opérations en file d'attente.
 */

const { createApp, ref, onMounted } = Vue;

const BandeauConnexion = {
    setup() {
        const enLigne = ref(navigator.onLine);
        const operationsEnAttente = ref(0);

        window.addEventListener("online", () => (enLigne.value = true));
        window.addEventListener("offline", () => (enLigne.value = false));

        onMounted(() => {
            window.SIHLSync.fileOperations.surChangement((n) => (operationsEnAttente.value = n));
            window.SIHLSync.fileOperations._rafraichirCompteur();
        });

        return { enLigne, operationsEnAttente };
    },
    template: `
        <div :class="['bandeau-connexion', enLigne ? 'en-ligne' : 'hors-ligne']">
            <span>{{ enLigne ? 'Connecté au serveur local' : 'Hors connexion — mode dégradé' }}</span>
            <span v-if="operationsEnAttente > 0">
                {{ operationsEnAttente }} opération(s) en attente de synchronisation
            </span>
        </div>
    `,
};

const AppSIHL = {
    components: { BandeauConnexion },
    template: `
        <BandeauConnexion />
        <main class="contenu">
            <h1>SIHL — Accueil</h1>
            <p>Coquille PWA de démarrage. Brancher ici les écrans des modules
               M1 à M7 (accueil, caisse, consultation, labo, pharmacie,
               hospitalisation, rapports).</p>
        </main>
    `,
};

createApp(AppSIHL).mount("#app");
