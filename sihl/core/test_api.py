import pytest
from django.conf import settings
from django.utils import timezone

from .models import JournalAudit, Utilisateur


@pytest.mark.django_db
class TestConnexion:
    def test_connexion_reussie(self, api_client, utilisateur):
        reponse = api_client.post(
            "/api/connexion/", {"username": "agent", "password": "motdepasse-robuste-1"}
        )
        assert reponse.status_code == 200
        assert reponse.data["username"] == "agent"

    def test_mot_de_passe_incorrect_incremente_echecs(self, api_client, utilisateur):
        reponse = api_client.post("/api/connexion/", {"username": "agent", "password": "faux"})
        assert reponse.status_code == 401
        utilisateur.refresh_from_db()
        assert utilisateur.echecs_authentification == 1

    def test_verrouillage_apres_echecs_repetes(self, api_client, utilisateur):
        for _ in range(settings.MAX_ECHECS_AUTHENTIFICATION):
            api_client.post("/api/connexion/", {"username": "agent", "password": "faux"})

        utilisateur.refresh_from_db()
        assert utilisateur.verrouille_jusqu_a is not None
        assert utilisateur.verrouille_jusqu_a > timezone.now()

        # Même avec le bon mot de passe, le compte reste verrouillé.
        reponse = api_client.post(
            "/api/connexion/", {"username": "agent", "password": "motdepasse-robuste-1"}
        )
        assert reponse.status_code == 423

    def test_connexion_reussie_reinitialise_les_echecs(self, api_client, utilisateur):
        api_client.post("/api/connexion/", {"username": "agent", "password": "faux"})
        api_client.post("/api/connexion/", {"username": "agent", "password": "motdepasse-robuste-1"})
        utilisateur.refresh_from_db()
        assert utilisateur.echecs_authentification == 0

    def test_deconnexion(self, client_authentifie):
        reponse = client_authentifie.post("/api/deconnexion/")
        assert reponse.status_code == 204


@pytest.mark.django_db
class TestRBACEndpoints:
    def test_utilisateur_non_admin_ne_peut_pas_lister_les_comptes(self, api_client, utilisateur):
        api_client.force_authenticate(user=utilisateur)
        reponse = api_client.get("/api/utilisateurs/")
        assert reponse.status_code == 403

    def test_superutilisateur_peut_lister_les_comptes(self, client_authentifie):
        reponse = client_authentifie.get("/api/utilisateurs/")
        assert reponse.status_code == 200

    def test_anonyme_refuse_sur_moi(self, api_client):
        reponse = api_client.get("/api/moi/")
        assert reponse.status_code == 403

    def test_journal_audit_lecture_seule_via_api(self, client_authentifie, superutilisateur):
        JournalAudit.enregistrer(auteur=superutilisateur, entite="Patient", entite_id=1, action="creation")
        reponse = client_authentifie.get("/api/journal-audit/")
        assert reponse.status_code == 200
        assert reponse.data["count"] == 1
