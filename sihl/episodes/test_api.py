import pytest


@pytest.mark.django_db
class TestEpisodeAPI:
    def test_creation_episode_via_api(self, client_authentifie, patient):
        reponse = client_authentifie.post(
            "/api/episodes/", {"patient": patient.pk, "type_episode": "AMBULATOIRE"}
        )
        assert reponse.status_code == 201
        assert reponse.data["numero"].startswith("EP-")
        assert reponse.data["montant_du"] == "0.00"

    def test_montant_du_et_paye_en_lecture_seule(self, client_authentifie, episode):
        reponse = client_authentifie.patch(
            f"/api/episodes/{episode.pk}/", {"montant_du": "999999.00"}
        )
        assert reponse.status_code == 200
        episode.refresh_from_db()
        assert episode.montant_du == 0

    def test_filtre_par_patient(self, client_authentifie, episode, patient):
        reponse = client_authentifie.get("/api/episodes/", {"patient": patient.pk})
        assert reponse.status_code == 200
        assert reponse.data["count"] == 1

    def test_anonyme_refuse(self, api_client, episode):
        reponse = api_client.get("/api/episodes/")
        assert reponse.status_code == 403
