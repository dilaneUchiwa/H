(function () {
"use strict";
/**
 * Coquille applicative : mise en page (barre latérale + contenu), routage,
 * authentification. Vue 3 sans étape de compilation (chapitre 4.1).
 */

const { createApp, ref, reactive, onMounted, computed } = Vue;

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
            <span class="bandeau-connexion__point"></span>
            <span>{{ enLigne ? 'Connecté au serveur local' : 'Hors connexion — mode dégradé' }}</span>
            <span v-if="operationsEnAttente > 0" class="bandeau-connexion__attente">
                {{ operationsEnAttente }} en attente
            </span>
        </div>
    `,
};

// Groupes de navigation, dans l'ordre du circuit patient (chapitre 5.1) :
// M1 (identification) en premier, M8 (administration) transverse en dernier.
const GROUPES_NAV = [
    {
        titre: "Tableau de bord",
        liens: [{ route: "accueil", label: "Accueil", icone: "🏠" }],
    },
    {
        titre: "M1 · Identification",
        liens: [
            { route: "patients", label: "Patients", icone: "🧑‍🤝‍🧑" },
            { route: "episodes", label: "Épisodes de soins", icone: "📋" },
        ],
    },
    {
        titre: "M5 · Caisse et facturation",
        liens: [
            { route: "tarifs", label: "Tarifs", icone: "💰" },
            { route: "actesFactures", label: "Actes facturés", icone: "🧾" },
            { route: "paiements", label: "Paiements", icone: "💳" },
            { route: "journalCaisse", label: "Journal de caisse", icone: "📒" },
        ],
    },
    {
        titre: "M2 · Consultation",
        liens: [
            { route: "consultations", label: "Consultations", icone: "🩺" },
            { route: "allergies", label: "Allergies", icone: "⚠️" },
            { route: "diagnosticsCim11", label: "Nomenclature CIM-11", icone: "📖" },
        ],
    },
    {
        titre: "M3 · Prescription et labo",
        liens: [
            { route: "prescriptions", label: "Prescriptions", icone: "📝" },
            { route: "lignesPrescription", label: "Lignes de prescription", icone: "📄" },
            { route: "catalogueExamens", label: "Catalogue examens", icone: "🧪" },
            { route: "examensLabo", label: "Examens en cours", icone: "🔬" },
            { route: "resultatsExamens", label: "Résultats", icone: "📊" },
        ],
    },
    {
        titre: "M4 · Pharmacie et stocks",
        liens: [
            { route: "medicaments", label: "Médicaments", icone: "💊" },
            { route: "lots", label: "Lots pharmaceutiques", icone: "📦" },
            { route: "mouvementsStock", label: "Mouvements de stock", icone: "↕️" },
        ],
    },
    {
        titre: "M6 · Hospitalisation",
        liens: [
            { route: "services", label: "Services", icone: "🏥" },
            { route: "lits", label: "Lits", icone: "🛏️" },
            { route: "sejours", label: "Séjours", icone: "📅" },
            { route: "soinsQuotidiens", label: "Soins quotidiens", icone: "🗓️" },
        ],
    },
    {
        titre: "M7 · Rapports",
        liens: [{ route: "rapports", label: "Rapports et export", icone: "📈" }],
    },
    {
        titre: "M8 · Administration",
        liens: [
            { route: "utilisateurs", label: "Utilisateurs", icone: "👤" },
            { route: "roles", label: "Rôles", icone: "🔐" },
            { route: "journalAudit", label: "Journal d'audit", icone: "🗂️" },
        ],
    },
];

const AppSIHL = {
    components: { BandeauConnexion },
    setup() {
        const utilisateur = ref(null);
        const chargementAuth = ref(true);
        const routeActuelle = ref("accueil");
        const menuMobileOuvert = ref(false);

        function resoudreRoute() {
            const hash = window.location.hash.replace(/^#\/?/, "");
            routeActuelle.value = hash || "accueil";
            menuMobileOuvert.value = false;
        }
        window.addEventListener("hashchange", resoudreRoute);

        async function chargerUtilisateur() {
            try {
                utilisateur.value = await SIHLApi.api("/moi/");
            } catch (e) {
                utilisateur.value = null;
            } finally {
                chargementAuth.value = false;
            }
        }

        function surConnexion(u) {
            utilisateur.value = u;
        }

        async function deconnexion() {
            try {
                await SIHLApi.api("/deconnexion/", { methode: "POST" });
            } catch (e) {
                // déjà déconnecté côté serveur : on nettoie quand même l'état local.
            }
            utilisateur.value = null;
        }

        onMounted(() => {
            resoudreRoute();
            chargerUtilisateur();
        });

        const composantPage = computed(() => {
            const pagesSpeciales = {
                accueil: window.SIHLScreens.PageTableauDeBord,
                patients: window.SIHLScreens.PagePatients,
                rapports: window.SIHLScreens.PageRapports,
            };
            return pagesSpeciales[routeActuelle.value] || null;
        });

        const configCrud = computed(() => window.SIHLConfigs[routeActuelle.value] || null);

        const titrePage = computed(() => {
            for (const groupe of GROUPES_NAV) {
                const lien = groupe.liens.find((l) => l.route === routeActuelle.value);
                if (lien) return lien.label;
            }
            return "SIHL";
        });

        const initialesUtilisateur = computed(() => {
            if (!utilisateur.value) return "";
            const { first_name: prenom, last_name: nom, username } = utilisateur.value;
            if (prenom || nom) return `${(prenom || "")[0] || ""}${(nom || "")[0] || ""}`.toUpperCase();
            return (username || "?").slice(0, 2).toUpperCase();
        });

        return {
            utilisateur,
            chargementAuth,
            routeActuelle,
            menuMobileOuvert,
            groupes: GROUPES_NAV,
            surConnexion,
            deconnexion,
            composantPage,
            configCrud,
            titrePage,
            initialesUtilisateur,
        };
    },
    template: `
        <template v-if="chargementAuth">
            <div class="ecran-chargement">Chargement…</div>
        </template>
        <template v-else-if="!utilisateur">
            <PageConnexion @connecte="surConnexion" />
        </template>
        <template v-else>
            <div class="mise-en-page" :class="{ 'mise-en-page--menu-ouvert': menuMobileOuvert }">
                <aside class="barre-laterale">
                    <div class="barre-laterale__entete">
                        <span class="barre-laterale__marque">S</span>
                        <div>
                            <span class="barre-laterale__logo">SIHL</span>
                            <span class="barre-laterale__soustitre">Système Info. Hospitalier Léger</span>
                        </div>
                    </div>
                    <nav class="barre-laterale__nav">
                        <div v-for="groupe in groupes" :key="groupe.titre" class="nav-groupe">
                            <p class="nav-groupe__titre">{{ groupe.titre }}</p>
                            <a
                                v-for="lien in groupe.liens"
                                :key="lien.route"
                                :href="'#/' + lien.route"
                                class="nav-lien"
                                :class="{ 'nav-lien--actif': routeActuelle === lien.route }"
                            >
                                <span class="nav-lien__icone">{{ lien.icone }}</span>
                                {{ lien.label }}
                            </a>
                        </div>
                    </nav>
                </aside>

                <div class="zone-principale">
                    <BandeauConnexion />
                    <header class="entete-app">
                        <button class="btn-menu-mobile" @click="menuMobileOuvert = !menuMobileOuvert">☰</button>
                        <h2 class="entete-app__titre">{{ titrePage }}</h2>
                        <div class="entete-app__utilisateur">
                            <span class="avatar">{{ initialesUtilisateur }}</span>
                            <span>{{ utilisateur.first_name || utilisateur.username }}</span>
                            <button class="btn btn--discret btn--mini" @click="deconnexion">Déconnexion</button>
                        </div>
                    </header>
                    <main class="contenu">
                        <component :is="composantPage" v-if="composantPage" :utilisateur="utilisateur" />
                        <SIHLPageCrud v-else-if="configCrud" :config="configCrud" />
                        <div v-else class="carte">Module en cours de construction.</div>
                    </main>
                </div>
            </div>
        </template>
    `,
};

document.addEventListener("DOMContentLoaded", () => {
    const app = createApp(AppSIHL);
    app.component("PageConnexion", window.SIHLScreens.PageConnexion);
    app.component("SIHLPageCrud", window.SIHLPages.PageCrud);
    app.mount("#app");
});

})();
