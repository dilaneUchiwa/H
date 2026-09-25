"""
Détection de doublons et fusion de fiches — chapitre 3.7.2/3.7.3.

Règle absolue du mémoire : **aucune fusion automatique**. Cette couche ne
fait que scorer des candidats ; la décision de fusionner reste humaine.
"""

from __future__ import annotations

import dataclasses
import datetime

from django.conf import settings
from django.db import transaction
from django.db.models import Q

from .models import CorrespondanceGraphie, FusionPatient, Patient
from .phonetique import cle_phonetique, similarite_phonetique


@dataclasses.dataclass
class CandidatDoublon:
    patient: Patient
    score: float
    details: dict[str, float]


def _graphie_canonique(nom: str) -> str:
    correspondance = CorrespondanceGraphie.objects.filter(graphie__iexact=nom).first()
    return correspondance.graphie_canonique if correspondance else nom


def _similarite_date_naissance(a: datetime.date | None, b: datetime.date | None) -> float:
    if not a or not b:
        return 0.0
    ecart_jours = abs((a - b).days)
    if ecart_jours == 0:
        return 1.0
    if ecart_jours <= 31:  # tolérance : âge souvent estimé
        return 0.7
    if ecart_jours <= 366:
        return 0.3
    return 0.0


def _similarite_telephone(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return 1.0 if a.strip() == b.strip() else 0.0


def rechercher_doublons(
    nom: str,
    prenom: str,
    date_naissance: datetime.date | None = None,
    telephone: str = "",
    exclure_pk: int | None = None,
) -> list[CandidatDoublon]:
    """
    Combine les trois critères du mémoire (chapitre 3.7.2) :
    similarité phonétique du nom, proximité de la date de naissance,
    identité du numéro de téléphone — pondérés selon DECISIONS.md #7.
    """
    nom_canonique = _graphie_canonique(nom)
    cle_recherche = cle_phonetique(nom_canonique)

    requete = Patient.objects.filter(actif=True)
    if exclure_pk:
        requete = requete.exclude(pk=exclure_pk)

    candidats_potentiels = requete.filter(
        Q(cle_phonetique=cle_recherche) | Q(telephone=telephone) if telephone else Q(cle_phonetique=cle_recherche)
    )

    resultats: list[CandidatDoublon] = []
    for candidat in candidats_potentiels:
        score_phonetique = similarite_phonetique(nom_canonique, prenom, candidat.nom, candidat.prenom)
        score_naissance = _similarite_date_naissance(date_naissance, candidat.date_naissance)
        score_telephone = _similarite_telephone(telephone, candidat.telephone)

        score = (
            score_phonetique * settings.DOUBLON_POIDS_PHONETIQUE
            + score_telephone * settings.DOUBLON_POIDS_TELEPHONE
            + score_naissance * settings.DOUBLON_POIDS_NAISSANCE
        )

        if score >= settings.DOUBLON_SEUIL_ALERTE:
            resultats.append(
                CandidatDoublon(
                    patient=candidat,
                    score=round(score, 3),
                    details={
                        "phonetique": score_phonetique,
                        "date_naissance": score_naissance,
                        "telephone": score_telephone,
                    },
                )
            )

    resultats.sort(key=lambda c: c.score, reverse=True)
    return resultats


@transaction.atomic
def fusionner_patients(*, absorbe: Patient, cible: Patient, auteur) -> FusionPatient:
    """
    Transfère tous les épisodes vers la fiche cible, désactive la fiche
    absorbée avec renvoi vers la cible, journalise l'opération.
    Réversible pendant la période paramétrée (chapitre 3.7.3).
    """
    if absorbe.pk == cible.pk:
        raise ValueError("Impossible de fusionner un patient avec lui-même.")

    for champ in ("episodes",):
        related_manager = getattr(absorbe, champ, None)
        if related_manager is not None:
            related_manager.all().update(patient=cible)

    absorbe.actif = False
    absorbe.fusionne_vers = cible
    absorbe.save(update_fields=["actif", "fusionne_vers"])

    fusion = FusionPatient.objects.create(patient_absorbe=absorbe, patient_cible=cible, auteur=auteur)

    from sihl.core.models import JournalAudit

    JournalAudit.enregistrer(
        auteur=auteur,
        entite="Patient",
        entite_id=cible.pk,
        action="fusion",
        valeurs_avant={"absorbe": absorbe.ipp},
        valeurs_apres={"cible": cible.ipp},
    )
    return fusion


@transaction.atomic
def annuler_fusion(fusion: FusionPatient, *, auteur) -> None:
    if not fusion.reversible():
        raise ValueError("Le délai de réversibilité de cette fusion est dépassé.")

    absorbe = fusion.patient_absorbe
    absorbe.actif = True
    absorbe.fusionne_vers = None
    absorbe.save(update_fields=["actif", "fusionne_vers"])

    for champ in ("episodes",):
        related_manager = getattr(fusion.patient_cible, champ, None)
        if related_manager is not None:
            related_manager.filter(patient=fusion.patient_cible).update(patient=absorbe)

    fusion.annulee = True
    from django.utils import timezone

    fusion.annulee_le = timezone.now()
    fusion.save(update_fields=["annulee", "annulee_le"])

    from sihl.core.models import JournalAudit

    JournalAudit.enregistrer(
        auteur=auteur,
        entite="Patient",
        entite_id=absorbe.pk,
        action="annulation_fusion",
        valeurs_avant=None,
        valeurs_apres={"restaure": absorbe.ipp},
    )
