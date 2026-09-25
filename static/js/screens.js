(function () {
"use strict";
/**
 * Écrans spécifiques qui ne rentrent pas dans le CRUD générique :
 * connexion, tableau de bord, identification patient (doublons/fusion),
 * rapports et export DHIS2.
 */

const { ref, reactive, onMounted } = Vue;

const PageConnexion = {
    emits: ["connecte"],
    setup(props, { emit }) {
        const identifiant = ref("");
        const motDePasse = ref("");
        const erreur = ref("");
        const enCours = ref(false);

        async function soumettre() {
            erreur.value = "";
            enCours.value = true;
            try {
                const utilisateur = await SIHLApi.api("/connexion/", {
                    methode: "POST",
                    corps: { username: identifiant.value, password: motDePasse.value },
                });
                emit("connecte", utilisateur);
            } catch (e) {
                erreur.value = e.message || "Connexion refusée.";
            } finally {
                enCours.value = false;
            }
        }

        return { identifiant, motDePasse, erreur, enCours, soumettre };
    },
    template: `
    <div class="ecran-connexion">
        <form class="carte carte--connexion" @submit.prevent="soumettre">
            <div class="ecran-connexion__marque">
                <span class="ecran-connexion__logo">S</span>
                <div>
                    <h1>SIHL</h1>
                    <p class="page-crud__soustitre">Système d'Information Hospitalier Léger</p>
                </div>
            </div>
            <label>Identifiant
                <input v-model="identifiant" required autofocus autocomplete="username" />
            </label>
            <label>Mot de passe
                <input v-model="motDePasse" type="password" required autocomplete="current-password" />
            </label>
            <p v-if="erreur" class="alerte alerte--erreur">{{ erreur }}</p>
            <button class="btn btn--primaire btn--large" type="submit" :disabled="enCours">
                {{ enCours ? 'Connexion…' : 'Se connecter' }}
            </button>
        </form>
    </div>
    `,
};

const PageTableauDeBord = {
    props: { utilisateur: Object },
    setup() {
        const stats = reactive({
            patients: null,
            episodesOuverts: null,
            litsOccupes: null,
            prescriptionsEnAttente: null,
        });
        const erreur = ref("");

        async function charger() {
            try {
                const [patients, episodes, lits, prescriptions] = await Promise.all([
                    SIHLApi.apiListe("/patients/"),
                    SIHLApi.apiListe("/episodes/", { statut: "OUVERT" }),
                    SIHLApi.apiListe("/lits/", { statut: "OCCUPE" }),
                    SIHLApi.apiListe("/prescriptions/", { statut: "EN_ATTENTE" }),
                ]);
                stats.patients = patients.count;
                stats.episodesOuverts = episodes.count;
                stats.litsOccupes = lits.count;
                stats.prescriptionsEnAttente = prescriptions.count;
            } catch (e) {
                erreur.value = e.message;
            }
        }
        onMounted(charger);
        return { stats, erreur };
    },
    template: `
    <section>
        <header class="page-crud__entete">
            <div>
                <h1>Tableau de bord</h1>
                <p class="page-crud__soustitre">Bonjour {{ utilisateur ? (utilisateur.first_name || utilisateur.username) : '' }}.</p>
            </div>
        </header>
        <p v-if="erreur" class="alerte alerte--erreur">{{ erreur }}</p>
        <div class="grille-stats">
            <div class="carte carte--stat">
                <span class="carte--stat__valeur">{{ stats.patients ?? '…' }}</span>
                <span class="carte--stat__label">Patients enregistrés</span>
            </div>
            <div class="carte carte--stat">
                <span class="carte--stat__valeur">{{ stats.episodesOuverts ?? '…' }}</span>
                <span class="carte--stat__label">Épisodes ouverts</span>
            </div>
            <div class="carte carte--stat">
                <span class="carte--stat__valeur">{{ stats.litsOccupes ?? '…' }}</span>
                <span class="carte--stat__label">Lits occupés</span>
            </div>
            <div class="carte carte--stat">
                <span class="carte--stat__valeur">{{ stats.prescriptionsEnAttente ?? '…' }}</span>
                <span class="carte--stat__label">Prescriptions en attente</span>
            </div>
        </div>
        <div class="carte">
            <h2>Bienvenue sur le SIHL</h2>
            <p>Utilisez le menu à gauche pour naviguer entre les modules, dans l'ordre du circuit
               patient recommandé par le mémoire : identification, caisse, consultation, pharmacie
               et laboratoire, hospitalisation, puis rapports.</p>
        </div>
    </section>
    `,
};

const PagePatients = {
    setup() {
        const nom = ref("");
        const prenom = ref("");
        const telephone = ref("");
        const dateNaissance = ref("");
        const candidats = ref(null);
        const recherche = ref(false);
        const erreur = ref("");

        async function verifierDoublons() {
            erreur.value = "";
            recherche.value = true;
            try {
                const params = { nom: nom.value, prenom: prenom.value };
                if (telephone.value) params.telephone = telephone.value;
                if (dateNaissance.value) params.date_naissance = dateNaissance.value;
                candidats.value = await SIHLApi.api(
                    "/patients/verifier_doublons/?" + new URLSearchParams(params).toString()
                );
            } catch (e) {
                erreur.value = e.message;
            } finally {
                recherche.value = false;
            }
        }

        return { nom, prenom, telephone, dateNaissance, candidats, recherche, erreur, verifierDoublons, config: SIHLConfigs.patients };
    },
    components: { PageCrud: SIHLPages.PageCrud },
    template: `
    <section>
        <div class="carte">
            <h2>Détection de doublons avant création (chapitre 3.7.2)</h2>
            <p class="page-crud__soustitre">
                Combine similarité phonétique du nom, téléphone et date de naissance.
                Aucune fusion automatique : une alerte est présentée à l'agent au-delà du seuil.
            </p>
            <form class="formulaire__grille" @submit.prevent="verifierDoublons">
                <label>Nom <input v-model="nom" required /></label>
                <label>Prénom <input v-model="prenom" /></label>
                <label>Téléphone <input v-model="telephone" /></label>
                <label>Date de naissance <input v-model="dateNaissance" type="date" /></label>
                <div class="formulaire__actions">
                    <button class="btn btn--primaire" type="submit" :disabled="recherche">Vérifier</button>
                </div>
            </form>
            <p v-if="erreur" class="alerte alerte--erreur">{{ erreur }}</p>
            <div v-if="candidats && candidats.length === 0" class="alerte alerte--succes">
                Aucun doublon détecté au-delà du seuil.
            </div>
            <table v-if="candidats && candidats.length" class="table">
                <thead><tr><th>IPP</th><th>Nom</th><th>Prénom</th><th>Score</th></tr></thead>
                <tbody>
                    <tr v-for="c in candidats" :key="c.patient.id">
                        <td>{{ c.patient.ipp }}</td>
                        <td>{{ c.patient.nom }}</td>
                        <td>{{ c.patient.prenom }}</td>
                        <td>{{ (c.score * 100).toFixed(0) }}%</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <PageCrud :config="config" />
    </section>
    `,
};

const PageRapports = {
    setup() {
        const maintenant = new Date();
        const annee = ref(maintenant.getFullYear());
        const mois = ref(maintenant.getMonth() + 1);
        const rapport = ref(null);
        const erreur = ref("");
        const chargement = ref(false);

        async function generer() {
            erreur.value = "";
            chargement.value = true;
            try {
                rapport.value = await SIHLApi.api(
                    `/rapports/mensuel/?annee=${annee.value}&mois=${mois.value}`
                );
            } catch (e) {
                erreur.value = e.message;
            } finally {
                chargement.value = false;
            }
        }

        function exporterCsv() {
            window.open(`/api/rapports/export-dhis2/?annee=${annee.value}&mois=${mois.value}`, "_blank");
        }

        onMounted(generer);
        return { annee, mois, rapport, erreur, chargement, generer, exporterCsv, formaterMontant: SIHLFormat.montant };
    },
    template: `
    <section>
        <header class="page-crud__entete">
            <div>
                <h1>Rapports et interopérabilité</h1>
                <p class="page-crud__soustitre">
                    Agrégats calculés comme sous-produit automatique des données transactionnelles
                    (chapitre 4.6) — jamais de données individuelles transmises.
                </p>
            </div>
        </header>
        <div class="carte">
            <form class="formulaire__grille" @submit.prevent="generer">
                <label>Année <input v-model.number="annee" type="number" /></label>
                <label>Mois <input v-model.number="mois" type="number" min="1" max="12" /></label>
                <div class="formulaire__actions">
                    <button class="btn btn--primaire" type="submit">Générer</button>
                    <button class="btn btn--discret" type="button" @click="exporterCsv">Exporter CSV (DHIS2)</button>
                </div>
            </form>
        </div>
        <p v-if="erreur" class="alerte alerte--erreur">{{ erreur }}</p>
        <div v-if="rapport" class="grille-stats">
            <div class="carte carte--stat">
                <span class="carte--stat__valeur">{{ rapport.nombre_consultations }}</span>
                <span class="carte--stat__label">Consultations</span>
            </div>
            <div class="carte carte--stat">
                <span class="carte--stat__valeur">{{ rapport.nombre_admissions }}</span>
                <span class="carte--stat__label">Admissions</span>
            </div>
            <div class="carte carte--stat">
                <span class="carte--stat__valeur">{{ rapport.nombre_sorties }}</span>
                <span class="carte--stat__label">Sorties</span>
            </div>
            <div class="carte carte--stat">
                <span class="carte--stat__valeur">{{ formaterMontant(rapport.recettes_totales) }}</span>
                <span class="carte--stat__label">Recettes totales</span>
            </div>
        </div>
        <div class="carte" v-if="rapport && rapport.diagnostics_frequents.length">
            <h2>Diagnostics les plus fréquents</h2>
            <table class="table">
                <thead><tr><th>Code CIM-11</th><th>Libellé</th><th>Nombre</th></tr></thead>
                <tbody>
                    <tr v-for="d in rapport.diagnostics_frequents" :key="d.code_cim11__code">
                        <td>{{ d.code_cim11__code }}</td>
                        <td>{{ d.code_cim11__libelle }}</td>
                        <td>{{ d.nombre }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>
    `,
};

window.SIHLScreens = { PageConnexion, PageTableauDeBord, PagePatients, PageRapports };

})();
