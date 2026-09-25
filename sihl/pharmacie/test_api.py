import datetime

import pytest

from .models import LotPharmaceutique


@pytest.mark.django_db
class TestMedicamentAPI:
    def test_creation_lot_genere_mouvement_entree(self, client_authentifie, medicament):
        reponse = client_authentifie.post(
            "/api/lots-pharmaceutiques/",
            {
                "medicament": medicament.pk,
                "numero_lot": "L2026-002",
                "date_peremption": (datetime.date.today() + datetime.timedelta(days=200)).isoformat(),
                "quantite_initiale": 50,
                "fournisseur": "Central d'achat",
            },
        )
        assert reponse.status_code == 201
        lot = LotPharmaceutique.objects.get(pk=reponse.data["id"])
        assert lot.quantite_restante == 50
        assert lot.mouvements.count() == 1

    def test_alertes_peremption(self, client_authentifie, medicament):
        LotPharmaceutique.objects.create(
            medicament=medicament,
            numero_lot="L-BIENTOT-PERIME",
            date_peremption=datetime.date.today() + datetime.timedelta(days=5),
            quantite_initiale=10,
            quantite_restante=10,
        )
        reponse = client_authentifie.get("/api/lots-pharmaceutiques/alertes_peremption/")
        assert reponse.status_code == 200
        assert len(reponse.data) == 1

    def test_alertes_seuil(self, client_authentifie, medicament):
        reponse = client_authentifie.get("/api/medicaments/alertes_seuil/")
        assert reponse.status_code == 200
        assert any(m["id"] == medicament.pk for m in reponse.data)
