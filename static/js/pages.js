(function () {
"use strict";
/**
 * Composant CRUD générique : une configuration (colonnes, champs de
 * formulaire, endpoint) suffit à obtenir une page liste + création +
 * édition + suppression. Utilisé pour la majorité des modules M1-M8 afin
 * d'éviter de dupliquer la même mécanique 15 fois (chapitre 2, sobriété).
 */

const { reactive, ref, computed, onMounted, onBeforeUnmount, watch } = Vue;

function champVide(champs) {
    const obj = {};
    champs.forEach((c) => {
        obj[c.cle] = c.type === "checkbox" ? false : "";
    });
    return obj;
}

// Cache partagé {endpoint: {id: libellé}} : évite de re-télécharger le
// même objet (ex. le même patient) à chaque sélecteur ou cellule de tableau
// qui le référence.
const cacheEtiquettes = reactive({});

async function resoudreEtiquette(endpoint, id, labelFn) {
    if (id === null || id === undefined || id === "") return "";
    cacheEtiquettes[endpoint] = cacheEtiquettes[endpoint] || {};
    if (cacheEtiquettes[endpoint][id] !== undefined) return cacheEtiquettes[endpoint][id];
    try {
        const item = await SIHLApi.api(`${endpoint}${id}/`);
        const libelle = labelFn(item);
        cacheEtiquettes[endpoint][id] = libelle;
        return libelle;
    } catch (e) {
        cacheEtiquettes[endpoint][id] = `#${id}`;
        return `#${id}`;
    }
}

/**
 * Sélecteur de type "combobox" avec recherche : remplace les champs qui
 * demandaient jusqu'ici un ID numérique brut pour désigner un patient, un
 * épisode, un lot, etc. Recherche côté serveur quand l'endpoint le permet
 * (ex. ?q= pour les patients), sinon filtre côté client sur les éléments
 * les plus récents.
 */
const SelecteurRecherche = {
    props: {
        modelValue: { type: [Number, String], default: "" },
        endpoint: { type: String, required: true },
        labelFn: { type: Function, required: true },
        parametreRecherche: { type: String, default: "" },
        placeholder: { type: String, default: "Rechercher…" },
        requis: { type: Boolean, default: false },
    },
    emits: ["update:modelValue"],
    setup(props, { emit }) {
        const requete = ref("");
        const resultats = ref([]);
        const ouvert = ref(false);
        const chargement = ref(false);
        const etiquetteActuelle = ref("");
        let minuteur = null;

        async function afficherEtiquetteActuelle() {
            etiquetteActuelle.value = props.modelValue
                ? await resoudreEtiquette(props.endpoint, props.modelValue, props.labelFn)
                : "";
        }

        async function rechercher() {
            chargement.value = true;
            try {
                const params = props.parametreRecherche
                    ? { [props.parametreRecherche]: requete.value }
                    : {};
                const donnees = await SIHLApi.apiListe(props.endpoint, params);
                let items = donnees.results;
                if (!props.parametreRecherche && requete.value) {
                    const q = requete.value.toLowerCase();
                    items = items.filter((it) => props.labelFn(it).toLowerCase().includes(q));
                }
                resultats.value = items.slice(0, 15);
            } finally {
                chargement.value = false;
            }
        }

        function surSaisie() {
            ouvert.value = true;
            clearTimeout(minuteur);
            minuteur = setTimeout(rechercher, 250);
        }

        function surFocus() {
            ouvert.value = true;
            if (resultats.value.length === 0) rechercher();
        }

        function choisir(item) {
            emit("update:modelValue", item.id);
            etiquetteActuelle.value = props.labelFn(item);
            requete.value = "";
            ouvert.value = false;
        }

        function effacer() {
            emit("update:modelValue", "");
            etiquetteActuelle.value = "";
        }

        function surBlur() {
            // Laisse le temps au clic sur une option de s'exécuter avant fermeture.
            setTimeout(() => (ouvert.value = false), 150);
        }

        watch(() => props.modelValue, afficherEtiquetteActuelle);
        onMounted(afficherEtiquetteActuelle);
        onBeforeUnmount(() => clearTimeout(minuteur));

        return {
            requete,
            resultats,
            ouvert,
            chargement,
            etiquetteActuelle,
            surSaisie,
            surFocus,
            surBlur,
            choisir,
            effacer,
        };
    },
    template: `
    <div class="selecteur-recherche">
        <div v-if="modelValue && !ouvert" class="selecteur-recherche__valeur" @click="ouvert = true; surFocus()">
            <span>{{ etiquetteActuelle || ('#' + modelValue) }}</span>
            <button type="button" class="selecteur-recherche__effacer" @click.stop="effacer" title="Changer">✕</button>
        </div>
        <input
            v-else
            type="text"
            v-model="requete"
            :placeholder="placeholder"
            :required="requis && !modelValue"
            @input="surSaisie"
            @focus="surFocus"
            @blur="surBlur"
            autocomplete="off"
        />
        <ul v-if="ouvert && !modelValue" class="selecteur-recherche__liste">
            <li v-if="chargement" class="selecteur-recherche__info">Recherche…</li>
            <li v-else-if="resultats.length === 0" class="selecteur-recherche__info">Aucun résultat.</li>
            <li v-for="item in resultats" :key="item.id" @mousedown.prevent="choisir(item)">
                {{ labelFn(item) }}
            </li>
        </ul>
    </div>
    `,
};

const PageCrud = {
    components: { SelecteurRecherche },
    props: {
        config: { type: Object, required: true },
    },
    setup(props) {
        const items = ref([]);
        const total = ref(0);
        const chargement = ref(false);
        const erreur = ref("");
        const formulaireOuvert = ref(false);
        const enEdition = ref(null);
        const formData = reactive(champVide(props.config.champs || []));
        const messageAction = ref("");

        async function charger() {
            chargement.value = true;
            erreur.value = "";
            try {
                const donnees = await SIHLApi.apiListe(props.config.endpoint);
                items.value = donnees.results;
                total.value = donnees.count;
            } catch (e) {
                erreur.value = e.message;
            } finally {
                chargement.value = false;
            }
        }

        function ouvrirCreation() {
            Object.assign(formData, champVide(props.config.champs || []));
            enEdition.value = null;
            formulaireOuvert.value = true;
        }

        function ouvrirEdition(item) {
            (props.config.champs || []).forEach((c) => (formData[c.cle] = item[c.cle]));
            enEdition.value = item.id;
            formulaireOuvert.value = true;
        }

        function fermerFormulaire() {
            formulaireOuvert.value = false;
            erreur.value = "";
        }

        async function soumettre() {
            erreur.value = "";
            try {
                const corps = {};
                (props.config.champs || []).forEach((c) => {
                    let v = formData[c.cle];
                    // Un champ optionnel laissé vide ne doit pas être envoyé : DRF
                    // rejette "" pour les DateField/IntegerField (seul null est accepté).
                    if (v === "" && !c.requis) return;
                    if ((c.type === "number" || c.type === "recherche") && v !== "") v = Number(v);
                    corps[c.cle] = v;
                });
                if (enEdition.value) {
                    await SIHLApi.api(`${props.config.endpoint}${enEdition.value}/`, {
                        methode: "PATCH",
                        corps,
                    });
                    messageAction.value = "Modification enregistrée.";
                } else {
                    await SIHLApi.api(props.config.endpoint, { methode: "POST", corps });
                    messageAction.value = "Créé avec succès.";
                }
                formulaireOuvert.value = false;
                await charger();
            } catch (e) {
                erreur.value = (e.donnees && JSON.stringify(e.donnees)) || e.message;
            }
        }

        async function executerAction(action, item) {
            erreur.value = "";
            try {
                await action.executer(item);
                messageAction.value = action.messageSucces || "Action effectuée.";
                await charger();
            } catch (e) {
                erreur.value = (e.donnees && JSON.stringify(e.donnees)) || e.message;
            }
        }

        onMounted(charger);
        watch(() => props.config.endpoint, charger);

        return {
            items,
            total,
            chargement,
            erreur,
            formulaireOuvert,
            enEdition,
            formData,
            messageAction,
            charger,
            ouvrirCreation,
            ouvrirEdition,
            fermerFormulaire,
            soumettre,
            executerAction,
        };
    },
    template: `
    <section class="page-crud">
        <header class="page-crud__entete">
            <div>
                <h1>{{ config.titre }}</h1>
                <p class="page-crud__soustitre">{{ config.description }}</p>
            </div>
            <button v-if="!config.lectureSeule" class="btn btn--primaire" @click="ouvrirCreation">
                + Nouveau
            </button>
        </header>

        <p v-if="messageAction" class="alerte alerte--succes">{{ messageAction }}</p>
        <p v-if="erreur" class="alerte alerte--erreur">{{ erreur }}</p>

        <div v-if="formulaireOuvert" class="carte formulaire">
            <h2>{{ enEdition ? 'Modifier' : 'Nouveau' }}</h2>
            <form @submit.prevent="soumettre">
                <div class="formulaire__grille">
                    <label v-for="champ in config.champs" :key="champ.cle">
                        {{ champ.label }}
                        <SelecteurRecherche
                            v-if="champ.type === 'recherche'"
                            v-model="formData[champ.cle]"
                            :endpoint="champ.endpoint"
                            :label-fn="champ.labelFn"
                            :parametre-recherche="champ.parametreRecherche || ''"
                            :placeholder="champ.placeholder || 'Rechercher…'"
                            :requis="champ.requis"
                        />
                        <select v-else-if="champ.type === 'select'" v-model="formData[champ.cle]" :required="champ.requis">
                            <option value="" disabled>Choisir…</option>
                            <option v-for="opt in champ.options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                        </select>
                        <input v-else-if="champ.type === 'checkbox'" type="checkbox" v-model="formData[champ.cle]" />
                        <textarea v-else-if="champ.type === 'textarea'" v-model="formData[champ.cle]"></textarea>
                        <input v-else :type="champ.type || 'text'" v-model="formData[champ.cle]" :required="champ.requis" />
                    </label>
                </div>
                <div class="formulaire__actions">
                    <button type="submit" class="btn btn--primaire">Enregistrer</button>
                    <button type="button" class="btn btn--discret" @click="fermerFormulaire">Annuler</button>
                </div>
            </form>
        </div>

        <div class="carte">
          <div class="table-scroll">
            <p v-if="chargement" class="etat-chargement"><span class="spinner"></span> Chargement…</p>
            <p v-else-if="items.length === 0" class="page-crud__vide">Aucun élément pour l'instant.</p>
            <table v-else class="table">
                <thead>
                    <tr>
                        <th v-for="col in config.colonnes" :key="col.cle">{{ col.label }}</th>
                        <th v-if="!config.lectureSeule || config.actions">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="item in items" :key="item.id">
                        <td v-for="col in config.colonnes" :key="col.cle">
                            <span v-if="col.badge" :class="['badge', 'badge--' + (item[col.cle] || '').toString().toLowerCase()]">
                                {{ col.format ? col.format(item[col.cle], item) : item[col.cle] }}
                            </span>
                            <EtiquetteFK
                                v-else-if="col.fk"
                                :endpoint="col.fk.endpoint"
                                :id="item[col.cle]"
                                :label-fn="col.fk.labelFn"
                            />
                            <span v-else>{{ col.format ? col.format(item[col.cle], item) : item[col.cle] }}</span>
                        </td>
                        <td class="table__actions">
                            <button v-if="!config.lectureSeule" class="btn btn--mini" @click="ouvrirEdition(item)">Modifier</button>
                            <button
                                v-for="action in (config.actions || [])"
                                :key="action.label"
                                class="btn btn--mini"
                                @click="executerAction(action, item)"
                            >{{ action.label }}</button>
                        </td>
                    </tr>
                </tbody>
            </table>
          </div>
            <p class="page-crud__total" v-if="items.length">{{ total }} au total</p>
        </div>
    </section>
    `,
};

// Petite cellule qui résout paresseusement "12" -> "SIH-2026-000004-31 — Ngoma Awa".
const EtiquetteFK = {
    props: { endpoint: String, id: [Number, String], labelFn: Function },
    setup(props) {
        const libelle = ref("…");
        async function charger() {
            libelle.value = await resoudreEtiquette(props.endpoint, props.id, props.labelFn);
        }
        watch(() => props.id, charger);
        onMounted(charger);
        return { libelle };
    },
    template: `<span>{{ libelle || '—' }}</span>`,
};

PageCrud.components.EtiquetteFK = EtiquetteFK;

window.SIHLPages = { PageCrud, champVide, SelecteurRecherche, EtiquetteFK, resoudreEtiquette };

})();
