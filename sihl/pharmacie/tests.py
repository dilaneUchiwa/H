import datetime

import pytest

from .models import LotPharmaceutique, Medicament, MouvementStock
from .services import DispensationImpossible, dispenser


@pytest.mark.django_db
class TestStockParLot:
    def test_medicament_ne_porte_pas_le_stock_directement(self):
        medicament = Medicament.objects.create(code="paracetamol", nom="Paracétamol", dosage="500mg")
        assert medicament.stock_courant == 0  # maintenu par trigger DB, pas par ce test SQLite

        lot = LotPharmaceutique.objects.create(
            medicament=medicament,
            numero_lot="L001",
            date_peremption=datetime.date.today() + datetime.timedelta(days=365),
            quantite_initiale=100,
            quantite_restante=0,
        )
        MouvementStock.objects.create(
            lot=lot, type_mouvement=MouvementStock.TypeMouvement.ENTREE, quantite=100
        )
        lot.refresh_from_db()
        assert lot.quantite_restante == 100

    def test_lot_perime(self):
        medicament = Medicament.objects.create(code="amoxicilline", nom="Amoxicilline")
        lot = LotPharmaceutique.objects.create(
            medicament=medicament,
            numero_lot="L002",
            date_peremption=datetime.date.today() - datetime.timedelta(days=1),
            quantite_initiale=10,
            quantite_restante=10,
        )
        assert lot.perime() is True

    def test_alerte_seuil(self):
        medicament = Medicament.objects.create(code="ibuprofene", nom="Ibuprofène", seuil_alerte=10)
        assert medicament.en_alerte_seuil() is True  # stock_courant part à 0


@pytest.mark.django_db
class TestDispensationService:
    def test_dispenser_decremente_et_journalise(self, prescription, medicament, lot_pharmaceutique, utilisateur):
        from sihl.prescriptions.models import LignePrescription

        ligne = LignePrescription.objects.create(
            prescription=prescription,
            type_ligne=LignePrescription.Type.MEDICAMENT,
            medicament=medicament,
            quantite=3,
        )
        mouvement = dispenser(ligne=ligne, lot=lot_pharmaceutique, quantite=3, utilisateur=utilisateur)

        assert mouvement.quantite == -3
        lot_pharmaceutique.refresh_from_db()
        assert lot_pharmaceutique.quantite_restante == 97
        ligne.refresh_from_db()
        assert ligne.honoree is True

    def test_dispenser_refuse_ligne_deja_honoree(self, prescription, medicament, lot_pharmaceutique, utilisateur):
        from sihl.prescriptions.models import LignePrescription

        ligne = LignePrescription.objects.create(
            prescription=prescription,
            type_ligne=LignePrescription.Type.MEDICAMENT,
            medicament=medicament,
            quantite=1,
            honoree=True,
        )
        with pytest.raises(DispensationImpossible):
            dispenser(ligne=ligne, lot=lot_pharmaceutique, quantite=1, utilisateur=utilisateur)

    def test_dispenser_refuse_lot_d_un_autre_medicament(self, prescription, medicament, lot_pharmaceutique, utilisateur):
        from sihl.prescriptions.models import LignePrescription

        autre_medicament = Medicament.objects.create(code="autre", nom="Autre médicament")
        ligne = LignePrescription.objects.create(
            prescription=prescription,
            type_ligne=LignePrescription.Type.MEDICAMENT,
            medicament=autre_medicament,
            quantite=1,
        )
        with pytest.raises(DispensationImpossible):
            dispenser(ligne=ligne, lot=lot_pharmaceutique, quantite=1, utilisateur=utilisateur)
