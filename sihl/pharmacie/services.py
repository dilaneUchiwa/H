"""
Dispensation — relie une ligne de prescription de type médicament à un lot
physique et décrémente le stock (chapitre 3.5.1, M4). Chaque dispensation
est une opération atomique et journalisée (traçabilité, chapitre 3.9).
"""

from __future__ import annotations

from django.db import transaction

from sihl.prescriptions.models import LignePrescription

from .models import LotPharmaceutique, MouvementStock


class DispensationImpossible(Exception):
    pass


@transaction.atomic
def dispenser(*, ligne: LignePrescription, lot: LotPharmaceutique, quantite: int, utilisateur) -> MouvementStock:
    if ligne.type_ligne != LignePrescription.Type.MEDICAMENT:
        raise DispensationImpossible("Cette ligne de prescription n'est pas un médicament.")
    if ligne.honoree:
        raise DispensationImpossible("Cette ligne de prescription a déjà été honorée.")
    if lot.medicament_id != ligne.medicament_id:
        raise DispensationImpossible("Le lot sélectionné ne correspond pas au médicament prescrit.")
    if lot.perime():
        raise DispensationImpossible("Ce lot est périmé : dispensation interdite.")
    if lot.quantite_restante < quantite:
        raise DispensationImpossible("Quantité insuffisante dans ce lot.")

    mouvement = MouvementStock.objects.create(
        lot=lot,
        type_mouvement=MouvementStock.TypeMouvement.SORTIE,
        quantite=-quantite,
        ligne_prescription=ligne,
        utilisateur=utilisateur,
        motif="Dispensation",
    )

    ligne.honoree = True
    ligne.save(update_fields=["honoree"])

    prescription = ligne.prescription
    lignes = prescription.lignes.all()
    if all(l.honoree for l in lignes):
        prescription.statut = prescription.Statut.HONOREE
    else:
        prescription.statut = prescription.Statut.PARTIELLE
    prescription.save(update_fields=["statut"])

    from sihl.core.models import JournalAudit

    JournalAudit.enregistrer(
        auteur=utilisateur,
        entite="LignePrescription",
        entite_id=ligne.pk,
        action="dispensation",
        valeurs_apres={"lot": lot.numero_lot, "quantite": quantite},
    )

    return mouvement
