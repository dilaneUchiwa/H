import pytest

from .models import LignePrescription


@pytest.mark.django_db
class TestPrescriptionAPI:
    def test_creation_prescription_definit_prescripteur(self, client_authentifie, consultation, superutilisateur):
        reponse = client_authentifie.post("/api/prescriptions/", {"consultation": consultation.pk})
        assert reponse.status_code == 201
        assert reponse.data["prescripteur"] == superutilisateur.pk
        assert reponse.data["statut"] == "EN_ATTENTE"


@pytest.mark.django_db
class TestDispensationAPI:
    def test_dispensation_decremente_le_lot_et_honore_la_ligne(
        self, client_authentifie, prescription, medicament, lot_pharmaceutique
    ):
        ligne = LignePrescription.objects.create(
            prescription=prescription,
            type_ligne=LignePrescription.Type.MEDICAMENT,
            medicament=medicament,
            quantite=5,
        )

        reponse = client_authentifie.post(
            f"/api/lignes-prescription/{ligne.pk}/dispenser/",
            {"lot": lot_pharmaceutique.pk, "quantite": 5},
        )
        assert reponse.status_code == 200
        assert reponse.data["honoree"] is True

        lot_pharmaceutique.refresh_from_db()
        assert lot_pharmaceutique.quantite_restante == 95

        prescription.refresh_from_db()
        assert prescription.statut == "HONOREE"

    def test_dispensation_refuse_si_quantite_insuffisante(
        self, client_authentifie, prescription, medicament, lot_pharmaceutique
    ):
        ligne = LignePrescription.objects.create(
            prescription=prescription,
            type_ligne=LignePrescription.Type.MEDICAMENT,
            medicament=medicament,
            quantite=500,
        )
        reponse = client_authentifie.post(
            f"/api/lignes-prescription/{ligne.pk}/dispenser/",
            {"lot": lot_pharmaceutique.pk, "quantite": 500},
        )
        assert reponse.status_code == 400
        ligne.refresh_from_db()
        assert ligne.honoree is False

    def test_dispensation_refuse_lot_perime(
        self, client_authentifie, prescription, medicament
    ):
        import datetime

        from sihl.pharmacie.models import LotPharmaceutique

        lot_perime = LotPharmaceutique.objects.create(
            medicament=medicament,
            numero_lot="L-PERIME",
            date_peremption=datetime.date.today() - datetime.timedelta(days=1),
            quantite_initiale=10,
            quantite_restante=10,
        )
        ligne = LignePrescription.objects.create(
            prescription=prescription,
            type_ligne=LignePrescription.Type.MEDICAMENT,
            medicament=medicament,
            quantite=1,
        )
        reponse = client_authentifie.post(
            f"/api/lignes-prescription/{ligne.pk}/dispenser/",
            {"lot": lot_perime.pk, "quantite": 1},
        )
        assert reponse.status_code == 400
