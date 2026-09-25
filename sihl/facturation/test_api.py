import pytest

from sihl.core.models import JournalAudit


@pytest.mark.django_db
class TestActeFacturableAPI:
    def test_creation_acte_via_api(self, client_authentifie, episode, tarif_acte):
        reponse = client_authentifie.post(
            "/api/actes-factures/", {"episode": episode.pk, "tarif": tarif_acte.pk, "quantite": 2}
        )
        assert reponse.status_code == 201
        assert reponse.data["montant"] == f"{tarif_acte.montant * 2:.2f}"

    def test_exoneration_journalisee(self, client_authentifie, episode, tarif_acte):
        reponse = client_authentifie.post(
            "/api/actes-factures/",
            {
                "episode": episode.pk,
                "tarif": tarif_acte.pk,
                "quantite": 1,
                "exoneration": True,
                "motif_exoneration": "Indigent",
            },
        )
        assert reponse.status_code == 201
        assert JournalAudit.objects.filter(action="exoneration").exists()


@pytest.mark.django_db
class TestPaiementAPI:
    def test_encaissement_definit_encaisse_par_et_journalise(self, client_authentifie, episode, superutilisateur):
        reponse = client_authentifie.post(
            "/api/paiements/", {"episode": episode.pk, "montant": 1500, "mode": "ESPECES"}
        )
        assert reponse.status_code == 201
        assert reponse.data["encaisse_par"] == superutilisateur.pk
        assert reponse.data["numero_recu"].startswith("RECU-")
        assert JournalAudit.objects.filter(action="encaissement").exists()

    def test_numero_recu_non_modifiable(self, client_authentifie, episode):
        reponse = client_authentifie.post(
            "/api/paiements/", {"episode": episode.pk, "montant": 100}
        )
        numero_initial = reponse.data["numero_recu"]
        reponse_maj = client_authentifie.patch(
            f"/api/paiements/{reponse.data['id']}/", {"numero_recu": "TRICHE-001"}
        )
        assert reponse_maj.data["numero_recu"] == numero_initial
