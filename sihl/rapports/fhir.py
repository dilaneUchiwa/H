"""
Projection FHIR minimale (chapitre 4.6.2, Tableau 17).

⚠️ Limite assumée par le mémoire : « sans implémenter un serveur FHIR
complet ». Ceci n'est PAS un serveur FHIR conforme (pas de _search complet,
pas de Bundle transaction, pas de validation de profil) mais une simple
projection en lecture seule de Patient / Encounter / Observation, classée
*Could* (Tableau 4). Voir DECISIONS.md #15.
"""

from __future__ import annotations

from sihl.consultations.models import Consultation
from sihl.episodes.models import EpisodeDeSoins
from sihl.patients.models import Patient


def patient_vers_fhir(patient: Patient) -> dict:
    return {
        "resourceType": "Patient",
        "id": str(patient.pk),
        "identifier": [{"system": "urn:sihl:ipp", "value": patient.ipp}],
        "name": [{"family": patient.nom, "given": [patient.prenom]}],
        "gender": {"M": "male", "F": "female"}.get(patient.sexe, "unknown"),
        "birthDate": patient.date_naissance.isoformat() if patient.date_naissance else None,
    }


def episode_vers_encounter(episode: EpisodeDeSoins) -> dict:
    return {
        "resourceType": "Encounter",
        "id": str(episode.pk),
        "status": "finished" if episode.statut == EpisodeDeSoins.Statut.CLOTURE else "in-progress",
        "class": {"code": episode.type_episode},
        "subject": {"reference": f"Patient/{episode.patient_id}"},
        "period": {
            "start": episode.date_ouverture.isoformat(),
            "end": episode.date_fermeture.isoformat() if episode.date_fermeture else None,
        },
    }


def consultation_vers_observations(consultation: Consultation) -> list[dict]:
    observations = []
    mesures = {
        "8310-5": ("temperature_c", "Cel"),
        "8867-4": ("frequence_cardiaque", "/min"),
        "9279-1": ("frequence_respiratoire", "/min"),
        "29463-7": ("poids_kg", "kg"),
    }
    for code_loinc, (champ, unite) in mesures.items():
        valeur = getattr(consultation, champ)
        if valeur is None:
            continue
        observations.append(
            {
                "resourceType": "Observation",
                "status": "final",
                "code": {"coding": [{"system": "http://loinc.org", "code": code_loinc}]},
                "subject": {"reference": f"Patient/{consultation.episode.patient_id}"},
                "encounter": {"reference": f"Encounter/{consultation.episode_id}"},
                "valueQuantity": {"value": float(valeur), "unit": unite},
            }
        )
    return observations
