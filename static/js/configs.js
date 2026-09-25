/**
 * Configuration des pages CRUD génériques, une par entité du domaine
 * (chapitre 3.5). Regroupées par module M1-M8 dans la barre latérale
 * (voir app.js) pour suivre l'ordre du circuit patient (chapitre 5.1).
 */

function dateCourte(v) {
    return v ? new Date(v).toLocaleDateString("fr-FR") : "—";
}
function dateHeureCourte(v) {
    return v ? new Date(v).toLocaleString("fr-FR") : "—";
}
function montant(v) {
    return v !== undefined && v !== null ? `${Number(v).toLocaleString("fr-FR")} FCFA` : "—";
}

window.SIHLConfigs = {
    // M1 — Identification
    patients: {
        titre: "Patients",
        description: "Identification unique (IPP), recherche multi-critères, détection de doublons.",
        endpoint: "/patients/",
        colonnes: [
            { cle: "ipp", label: "IPP" },
            { cle: "nom", label: "Nom" },
            { cle: "prenom", label: "Prénom" },
            { cle: "date_naissance", label: "Naissance", format: dateCourte },
            { cle: "telephone", label: "Téléphone" },
        ],
        champs: [
            { cle: "nom", label: "Nom", requis: true },
            { cle: "prenom", label: "Prénom", requis: true },
            {
                cle: "sexe",
                label: "Sexe",
                type: "select",
                requis: true,
                options: [
                    { value: "M", label: "Masculin" },
                    { value: "F", label: "Féminin" },
                    { value: "I", label: "Indéterminé" },
                ],
            },
            { cle: "date_naissance", label: "Date de naissance", type: "date" },
            { cle: "telephone", label: "Téléphone" },
            { cle: "adresse", label: "Adresse" },
        ],
    },

    // Épisodes de soins
    episodes: {
        titre: "Épisodes de soins",
        description: "Entité intermédiaire patient ↔ consultation : porte la facturation.",
        endpoint: "/episodes/",
        colonnes: [
            { cle: "numero", label: "Numéro" },
            { cle: "patient", label: "ID Patient" },
            { cle: "type_episode", label: "Type", badge: true },
            { cle: "statut", label: "Statut", badge: true },
            { cle: "montant_du", label: "Dû", format: montant },
            { cle: "montant_paye", label: "Payé", format: montant },
        ],
        champs: [
            { cle: "patient", label: "ID Patient (voir page Patients)", type: "number", requis: true },
            {
                cle: "type_episode",
                label: "Type",
                type: "select",
                requis: true,
                options: [
                    { value: "AMBULATOIRE", label: "Ambulatoire" },
                    { value: "HOSPITALISATION", label: "Hospitalisation" },
                    { value: "URGENCE", label: "Urgence" },
                ],
            },
        ],
    },

    // M2 — Consultation
    consultations: {
        titre: "Consultations",
        description: "Triage, anamnèse, examen, conclusion — historique complet par épisode.",
        endpoint: "/consultations/",
        colonnes: [
            { cle: "episode", label: "ID Épisode" },
            { cle: "date", label: "Date", format: dateHeureCourte },
            { cle: "motif", label: "Motif" },
            { cle: "conclusion", label: "Conclusion" },
        ],
        champs: [
            { cle: "episode", label: "ID Épisode", type: "number", requis: true },
            { cle: "motif", label: "Motif", requis: true },
            { cle: "temperature_c", label: "Température (°C)", type: "number" },
            { cle: "tension_arterielle_systolique", label: "TA systolique", type: "number" },
            { cle: "tension_arterielle_diastolique", label: "TA diastolique", type: "number" },
            { cle: "frequence_cardiaque", label: "Fréquence cardiaque", type: "number" },
            { cle: "poids_kg", label: "Poids (kg)", type: "number" },
            { cle: "anamnese", label: "Anamnèse", type: "textarea" },
            { cle: "examen_clinique", label: "Examen clinique", type: "textarea" },
            { cle: "conclusion", label: "Conclusion", type: "textarea" },
        ],
    },

    allergies: {
        titre: "Allergies",
        description: "Doivent rester visibles dans tout le dossier patient.",
        endpoint: "/allergies/",
        colonnes: [
            { cle: "patient", label: "ID Patient" },
            { cle: "libelle", label: "Allergie" },
            { cle: "severite", label: "Sévérité", badge: true },
        ],
        champs: [
            { cle: "patient", label: "ID Patient", type: "number", requis: true },
            { cle: "libelle", label: "Allergie", requis: true },
            {
                cle: "severite",
                label: "Sévérité",
                type: "select",
                options: [
                    { value: "LEGERE", label: "Légère" },
                    { value: "MODEREE", label: "Modérée" },
                    { value: "SEVERE", label: "Sévère" },
                ],
            },
        ],
    },

    diagnosticsCim11: {
        titre: "Nomenclature CIM-11",
        description: "Sous-ensemble local (import CSV, pas d'appel externe).",
        endpoint: "/diagnostics-cim11/",
        lectureSeule: true,
        colonnes: [
            { cle: "code", label: "Code" },
            { cle: "libelle", label: "Libellé" },
        ],
        champs: [],
    },

    // M3 — Prescription et laboratoire
    prescriptions: {
        titre: "Prescriptions",
        description: "Ordonnance DCI (médicaments) et examens de laboratoire.",
        endpoint: "/prescriptions/",
        colonnes: [
            { cle: "consultation", label: "ID Consultation" },
            { cle: "date", label: "Date", format: dateHeureCourte },
            { cle: "statut", label: "Statut", badge: true },
        ],
        champs: [{ cle: "consultation", label: "ID Consultation", type: "number", requis: true }],
    },

    lignesPrescription: {
        titre: "Lignes de prescription",
        description: "Détail par prescription : médicament ou examen, quantité.",
        endpoint: "/lignes-prescription/",
        colonnes: [
            { cle: "prescription", label: "ID Prescription" },
            { cle: "type_ligne", label: "Type", badge: true },
            { cle: "libelle_produit", label: "Produit" },
            { cle: "quantite", label: "Qté" },
            { cle: "honoree", label: "Honorée", format: (v) => (v ? "Oui" : "Non") },
        ],
        champs: [
            { cle: "prescription", label: "ID Prescription", type: "number", requis: true },
            {
                cle: "type_ligne",
                label: "Type",
                type: "select",
                requis: true,
                options: [
                    { value: "MEDICAMENT", label: "Médicament" },
                    { value: "EXAMEN", label: "Examen de laboratoire" },
                ],
            },
            { cle: "medicament", label: "ID Médicament (si médicament)", type: "number" },
            { cle: "examen", label: "ID Examen catalogue (si examen)", type: "number" },
            { cle: "posologie", label: "Posologie" },
            { cle: "quantite", label: "Quantité", type: "number", requis: true },
        ],
    },

    catalogueExamens: {
        titre: "Catalogue des examens",
        description: "Nomenclature de laboratoire et valeurs de référence.",
        endpoint: "/catalogue-examens/",
        lectureSeule: true,
        colonnes: [
            { cle: "code", label: "Code" },
            { cle: "libelle", label: "Libellé" },
            { cle: "unite", label: "Unité" },
            { cle: "valeur_reference_min", label: "Min" },
            { cle: "valeur_reference_max", label: "Max" },
        ],
        champs: [],
    },

    examensLabo: {
        titre: "Examens de laboratoire",
        description: "Suivi des examens prescrits jusqu'à validation du résultat.",
        endpoint: "/examens-labo/",
        colonnes: [
            { cle: "ligne_prescription", label: "ID Ligne prescription" },
            { cle: "catalogue", label: "ID Examen" },
            { cle: "statut", label: "Statut", badge: true },
            { cle: "demande_le", label: "Demandé le", format: dateHeureCourte },
        ],
        champs: [
            { cle: "ligne_prescription", label: "ID Ligne de prescription", type: "number", requis: true },
            { cle: "catalogue", label: "ID Examen (catalogue)", type: "number", requis: true },
        ],
    },

    resultatsExamens: {
        titre: "Résultats d'examens",
        description: "Valeur, unité, détection automatique hors référence.",
        endpoint: "/resultats-examens/",
        colonnes: [
            { cle: "examen", label: "ID Examen" },
            { cle: "valeur", label: "Valeur" },
            { cle: "unite", label: "Unité" },
            { cle: "hors_reference", label: "Hors référence", format: (v) => (v ? "⚠ Oui" : "Non") },
        ],
        champs: [
            { cle: "examen", label: "ID Examen", type: "number", requis: true },
            { cle: "valeur", label: "Valeur", requis: true },
            { cle: "unite", label: "Unité" },
            { cle: "critique", label: "Valeur critique", type: "checkbox" },
        ],
    },

    // M4 — Pharmacie et stocks
    medicaments: {
        titre: "Médicaments",
        description: "Catalogue DCI. Le stock est toujours porté par les lots, jamais ici.",
        endpoint: "/medicaments/",
        colonnes: [
            { cle: "code", label: "Code" },
            { cle: "nom", label: "Nom" },
            { cle: "dosage", label: "Dosage" },
            { cle: "stock_courant", label: "Stock courant" },
            { cle: "seuil_alerte", label: "Seuil d'alerte" },
        ],
        champs: [
            { cle: "code", label: "Code", requis: true },
            { cle: "denomination_commune", label: "DCI", requis: true },
            { cle: "nom", label: "Nom commercial", requis: true },
            { cle: "forme", label: "Forme" },
            { cle: "dosage", label: "Dosage" },
            { cle: "seuil_alerte", label: "Seuil d'alerte", type: "number" },
        ],
    },

    lots: {
        titre: "Lots pharmaceutiques",
        description: "Stock physique réel : péremption et quantité par lot.",
        endpoint: "/lots-pharmaceutiques/",
        colonnes: [
            { cle: "medicament", label: "ID Médicament" },
            { cle: "numero_lot", label: "N° de lot" },
            { cle: "date_peremption", label: "Péremption", format: dateCourte },
            { cle: "quantite_restante", label: "Qté restante" },
        ],
        champs: [
            { cle: "medicament", label: "ID Médicament", type: "number", requis: true },
            { cle: "numero_lot", label: "Numéro de lot", requis: true },
            { cle: "date_peremption", label: "Date de péremption", type: "date", requis: true },
            { cle: "quantite_initiale", label: "Quantité reçue", type: "number", requis: true },
            { cle: "fournisseur", label: "Fournisseur" },
        ],
    },

    mouvementsStock: {
        titre: "Mouvements de stock",
        description: "Entrées, sorties (dispensation), ajustements d'inventaire.",
        endpoint: "/mouvements-stock/",
        colonnes: [
            { cle: "lot", label: "ID Lot" },
            { cle: "type_mouvement", label: "Type", badge: true },
            { cle: "quantite", label: "Quantité" },
            { cle: "date", label: "Date", format: dateHeureCourte },
        ],
        champs: [
            { cle: "lot", label: "ID Lot", type: "number", requis: true },
            {
                cle: "type_mouvement",
                label: "Type",
                type: "select",
                requis: true,
                options: [
                    { value: "ENTREE", label: "Entrée" },
                    { value: "SORTIE", label: "Sortie" },
                    { value: "AJUSTEMENT", label: "Ajustement d'inventaire" },
                    { value: "PEREMPTION", label: "Retrait pour péremption" },
                ],
            },
            { cle: "quantite", label: "Quantité (négatif en sortie)", type: "number", requis: true },
            { cle: "motif", label: "Motif" },
        ],
    },

    // M5 — Caisse et facturation
    tarifs: {
        titre: "Tarifs des actes",
        description: "Nomenclature et tarification des prestations.",
        endpoint: "/tarifs-actes/",
        colonnes: [
            { cle: "code", label: "Code" },
            { cle: "libelle", label: "Libellé" },
            { cle: "montant", label: "Montant", format: montant },
            { cle: "actif", label: "Actif", format: (v) => (v ? "Oui" : "Non") },
        ],
        champs: [
            { cle: "code", label: "Code", requis: true },
            { cle: "libelle", label: "Libellé", requis: true },
            { cle: "montant", label: "Montant (FCFA)", type: "number", requis: true },
        ],
    },

    actesFactures: {
        titre: "Actes facturés",
        description: "Rattachement à l'épisode, exonérations tracées.",
        endpoint: "/actes-factures/",
        colonnes: [
            { cle: "episode", label: "ID Épisode" },
            { cle: "tarif", label: "ID Tarif" },
            { cle: "quantite", label: "Qté" },
            { cle: "montant", label: "Montant", format: montant },
            { cle: "exoneration", label: "Exonéré", format: (v) => (v ? "Oui" : "Non") },
        ],
        champs: [
            { cle: "episode", label: "ID Épisode", type: "number", requis: true },
            { cle: "tarif", label: "ID Tarif", type: "number", requis: true },
            { cle: "quantite", label: "Quantité", type: "number", requis: true },
            { cle: "exoneration", label: "Exonération", type: "checkbox" },
            { cle: "motif_exoneration", label: "Motif d'exonération" },
        ],
    },

    paiements: {
        titre: "Paiements",
        description: "Encaissement, reçu numéroté automatiquement.",
        endpoint: "/paiements/",
        colonnes: [
            { cle: "numero_recu", label: "N° Reçu" },
            { cle: "episode", label: "ID Épisode" },
            { cle: "montant", label: "Montant", format: montant },
            { cle: "mode", label: "Mode", badge: true },
            { cle: "date", label: "Date", format: dateHeureCourte },
        ],
        champs: [
            { cle: "episode", label: "ID Épisode", type: "number", requis: true },
            { cle: "montant", label: "Montant (FCFA)", type: "number", requis: true },
            {
                cle: "mode",
                label: "Mode de paiement",
                type: "select",
                options: [
                    { value: "ESPECES", label: "Espèces" },
                    { value: "MOBILE_MONEY", label: "Monnaie électronique" },
                    { value: "AUTRE", label: "Autre" },
                ],
            },
        ],
    },

    journalCaisse: {
        titre: "Journal de caisse",
        description: "Rapprochement quotidien : écart calculé automatiquement.",
        endpoint: "/journal-caisse/",
        colonnes: [
            { cle: "date_cloture", label: "Date", format: dateCourte },
            { cle: "montant_theorique", label: "Théorique", format: montant },
            { cle: "montant_compte", label: "Compté", format: montant },
            { cle: "ecart", label: "Écart", format: montant },
        ],
        champs: [
            { cle: "date_cloture", label: "Date de clôture", type: "date", requis: true },
            { cle: "montant_theorique", label: "Montant théorique", type: "number", requis: true },
            { cle: "montant_compte", label: "Montant compté", type: "number", requis: true },
        ],
    },

    // M6 — Hospitalisation
    services: {
        titre: "Services",
        description: "Table de paramétrage des services de l'établissement.",
        endpoint: "/services/",
        colonnes: [
            { cle: "code", label: "Code" },
            { cle: "nom", label: "Nom" },
            { cle: "actif", label: "Actif", format: (v) => (v ? "Oui" : "Non") },
        ],
        champs: [
            { cle: "code", label: "Code", requis: true },
            { cle: "nom", label: "Nom", requis: true },
        ],
    },

    lits: {
        titre: "Lits",
        description: "Plan des lits en temps réel par service.",
        endpoint: "/lits/",
        colonnes: [
            { cle: "service", label: "ID Service" },
            { cle: "numero", label: "Numéro" },
            { cle: "statut", label: "Statut", badge: true },
        ],
        champs: [
            { cle: "service", label: "ID Service", type: "number", requis: true },
            { cle: "numero", label: "Numéro de lit", requis: true },
        ],
    },

    sejours: {
        titre: "Séjours",
        description: "Admission, affectation lit, sortie avec mode et diagnostic.",
        endpoint: "/sejours/",
        colonnes: [
            { cle: "episode", label: "ID Épisode" },
            { cle: "lit", label: "ID Lit" },
            { cle: "date_admission", label: "Admission", format: dateHeureCourte },
            { cle: "date_sortie", label: "Sortie", format: dateHeureCourte },
            { cle: "mode_sortie", label: "Mode de sortie", badge: true },
        ],
        champs: [
            { cle: "episode", label: "ID Épisode", type: "number", requis: true },
            { cle: "lit", label: "ID Lit", type: "number", requis: true },
            { cle: "date_admission", label: "Date d'admission", type: "datetime-local", requis: true },
        ],
    },

    soinsQuotidiens: {
        titre: "Soins quotidiens",
        description: "Prescriptions et soins quotidiens du séjour.",
        endpoint: "/soins-quotidiens/",
        colonnes: [
            { cle: "sejour", label: "ID Séjour" },
            { cle: "date_heure", label: "Date", format: dateHeureCourte },
            { cle: "description", label: "Description" },
        ],
        champs: [
            { cle: "sejour", label: "ID Séjour", type: "number", requis: true },
            { cle: "date_heure", label: "Date et heure", type: "datetime-local", requis: true },
            { cle: "description", label: "Description", type: "textarea", requis: true },
        ],
    },

    // M8 — Administration
    utilisateurs: {
        titre: "Utilisateurs",
        description: "Comptes nominatifs (réservé aux administrateurs).",
        endpoint: "/utilisateurs/",
        lectureSeule: true,
        colonnes: [
            { cle: "username", label: "Identifiant" },
            { cle: "first_name", label: "Prénom" },
            { cle: "last_name", label: "Nom" },
            { cle: "is_active", label: "Actif", format: (v) => (v ? "Oui" : "Non") },
        ],
        champs: [],
    },

    roles: {
        titre: "Rôles",
        description: "Matrice de droits (RBAC) — Tableau 14 du mémoire.",
        endpoint: "/roles/",
        colonnes: [
            { cle: "code", label: "Code" },
            { cle: "libelle", label: "Libellé" },
            { cle: "acces_contenu_clinique", label: "Accès clinique", format: (v) => (v ? "Oui" : "Non") },
        ],
        champs: [
            { cle: "code", label: "Code", requis: true },
            { cle: "libelle", label: "Libellé", requis: true },
        ],
    },

    journalAudit: {
        titre: "Journal d'audit",
        description: "Trace inaltérable des opérations sensibles — écriture seule.",
        endpoint: "/journal-audit/",
        lectureSeule: true,
        colonnes: [
            { cle: "horodatage", label: "Horodatage", format: dateHeureCourte },
            { cle: "auteur", label: "Auteur" },
            { cle: "entite", label: "Entité" },
            { cle: "entite_id", label: "ID" },
            { cle: "action", label: "Action", badge: true },
        ],
        champs: [],
    },
};

window.SIHLFormat = { dateCourte, dateHeureCourte, montant };
