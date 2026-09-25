import pytest
from django.utils import timezone

from .models import Lit, Sejour


@pytest.mark.django_db
class TestSejourAPI:
    def test_admission_via_api(self, client_authentifie, episode, lit, superutilisateur):
        reponse = client_authentifie.post(
            "/api/sejours/",
            {"episode": episode.pk, "lit": lit.pk, "date_admission": timezone.now().isoformat()},
        )
        assert reponse.status_code == 201
        assert reponse.data["admis_par"] == superutilisateur.pk
        lit.refresh_from_db()
        assert lit.statut == Lit.Statut.OCCUPE

    def test_sortie_via_api_libere_le_lit(self, client_authentifie, episode, lit, utilisateur, diagnostic_cim11):
        sejour = Sejour.objects.create(
            episode=episode, lit=lit, date_admission=timezone.now(), admis_par=utilisateur
        )
        reponse = client_authentifie.post(
            f"/api/sejours/{sejour.pk}/sortie/",
            {"mode_sortie": "GUERISON", "diagnostic_sortie": diagnostic_cim11.pk},
        )
        assert reponse.status_code == 200
        assert reponse.data["mode_sortie"] == "GUERISON"
        lit.refresh_from_db()
        assert lit.statut == Lit.Statut.LIBRE

    def test_soin_quotidien_via_api(self, client_authentifie, episode, lit, utilisateur, superutilisateur):
        sejour = Sejour.objects.create(
            episode=episode, lit=lit, date_admission=timezone.now(), admis_par=utilisateur
        )
        reponse = client_authentifie.post(
            "/api/soins-quotidiens/",
            {"sejour": sejour.pk, "date_heure": timezone.now().isoformat(), "description": "Pansement"},
        )
        assert reponse.status_code == 201
        assert reponse.data["realise_par"] == superutilisateur.pk
