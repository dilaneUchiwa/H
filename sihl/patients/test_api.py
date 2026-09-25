import pytest

from .models import FusionPatient, Patient


@pytest.mark.django_db
class TestPatientAPI:
    def test_creation_patient_attribue_ipp(self, client_authentifie):
        reponse = client_authentifie.post(
            "/api/patients/", {"nom": "Kamdem", "prenom": "Paul", "sexe": "M"}
        )
        assert reponse.status_code == 201
        assert reponse.data["ipp"].startswith("SIH-")

    def test_recherche_multicriteres(self, client_authentifie, patient):
        reponse = client_authentifie.get("/api/patients/", {"q": "Ngoma"})
        assert reponse.status_code == 200
        assert reponse.data["count"] == 1
        assert reponse.data["results"][0]["ipp"] == patient.ipp

    def test_verifier_doublons_endpoint(self, client_authentifie, patient):
        reponse = client_authentifie.get(
            "/api/patients/verifier_doublons/",
            {"nom": "Noma", "prenom": "Awa", "telephone": "699000001"},
        )
        assert reponse.status_code == 200
        assert len(reponse.data) == 1
        assert reponse.data[0]["patient"]["ipp"] == patient.ipp

    def test_anonyme_refuse(self, api_client):
        reponse = api_client.get("/api/patients/")
        assert reponse.status_code == 403


@pytest.mark.django_db
class TestFusionAPI:
    def test_fusion_puis_annulation_via_api(self, client_authentifie):
        absorbe = Patient.objects.create(nom="Ngoma", prenom="Awa", sexe="F")
        cible = Patient.objects.create(nom="Ngoma", prenom="Awa Marie", sexe="F")

        reponse = client_authentifie.post(
            f"/api/patients/{absorbe.pk}/fusionner/", {"patient_cible": cible.pk}
        )
        assert reponse.status_code == 201
        absorbe.refresh_from_db()
        assert absorbe.actif is False
        assert absorbe.fusionne_vers_id == cible.pk

        fusion_id = reponse.data["id"]
        reponse_annulation = client_authentifie.post(f"/api/fusions-patients/{fusion_id}/annuler/")
        assert reponse_annulation.status_code == 200
        absorbe.refresh_from_db()
        assert absorbe.actif is True
        assert absorbe.fusionne_vers_id is None
        assert FusionPatient.objects.get(pk=fusion_id).annulee is True
