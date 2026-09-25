import pytest


@pytest.mark.django_db
class TestConsultationAPI:
    def test_creation_consultation_definit_le_medecin_connecte(self, client_authentifie, episode, superutilisateur):
        reponse = client_authentifie.post(
            "/api/consultations/", {"episode": episode.pk, "motif": "Douleur abdominale"}
        )
        assert reponse.status_code == 201
        assert reponse.data["medecin"] == superutilisateur.pk

    def test_allergies_visibles_dans_la_consultation(self, client_authentifie, episode, patient):
        client_authentifie.post("/api/allergies/", {"patient": patient.pk, "libelle": "Pénicilline"})
        reponse = client_authentifie.post(
            "/api/consultations/", {"episode": episode.pk, "motif": "Contrôle"}
        )
        assert reponse.status_code == 201
        assert any(a["libelle"] == "Pénicilline" for a in reponse.data["allergies_patient"])

    def test_diagnostic_cim11_lecture_seule_recherche(self, client_authentifie, diagnostic_cim11):
        reponse = client_authentifie.get("/api/diagnostics-cim11/")
        assert reponse.status_code == 200
        reponse_creation = client_authentifie.post(
            "/api/diagnostics-cim11/", {"code": "1B10", "libelle": "Test"}
        )
        assert reponse_creation.status_code == 405
