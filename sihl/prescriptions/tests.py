import pytest

from .models import LignePrescription


@pytest.mark.django_db
class TestLignePrescriptionModel:
    def test_libelle_produit_copie_a_l_ecriture(self, prescription, medicament):
        ligne = LignePrescription.objects.create(
            prescription=prescription,
            type_ligne=LignePrescription.Type.MEDICAMENT,
            medicament=medicament,
            quantite=2,
        )
        assert ligne.libelle_produit == medicament.nom

        # Intégrité historique : renommer le médicament ne change pas la ligne existante.
        medicament.nom = "Nouveau nom"
        medicament.save(update_fields=["nom"])
        ligne.refresh_from_db()
        assert ligne.libelle_produit != "Nouveau nom"
