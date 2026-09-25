import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestRapportsAPI:
    def test_rapport_mensuel_endpoint(self, client_authentifie):
        aujourdhui = timezone.now()
        reponse = client_authentifie.get(
            "/api/rapports/mensuel/", {"annee": aujourdhui.year, "mois": aujourdhui.month}
        )
        assert reponse.status_code == 200
        assert "nombre_consultations" in reponse.data

    def test_export_dhis2_endpoint_renvoie_csv(self, client_authentifie):
        aujourdhui = timezone.now()
        reponse = client_authentifie.get(
            "/api/rapports/export-dhis2/", {"annee": aujourdhui.year, "mois": aujourdhui.month}
        )
        assert reponse.status_code == 200
        assert reponse["Content-Type"] == "text/csv"

    def test_fhir_patient_endpoint(self, client_authentifie, patient):
        reponse = client_authentifie.get(f"/api/fhir/Patient/{patient.pk}/")
        assert reponse.status_code == 200
        assert reponse.data["resourceType"] == "Patient"

    def test_endpoints_refuses_sans_authentification(self, api_client, patient):
        reponse = api_client.get(f"/api/fhir/Patient/{patient.pk}/")
        assert reponse.status_code == 403
