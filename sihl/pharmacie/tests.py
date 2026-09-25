import datetime

import pytest

from .models import LotPharmaceutique, Medicament, MouvementStock


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
