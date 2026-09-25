import pytest

from .models import Lit, Sejour


@pytest.mark.django_db
class TestSejourModel:
    def test_admission_occupe_le_lit(self, episode, lit, utilisateur):
        from django.utils import timezone

        assert lit.statut == Lit.Statut.LIBRE
        Sejour.objects.create(episode=episode, lit=lit, date_admission=timezone.now(), admis_par=utilisateur)
        lit.refresh_from_db()
        assert lit.statut == Lit.Statut.OCCUPE

    def test_cloture_libere_le_lit(self, episode, lit, utilisateur, diagnostic_cim11):
        from django.utils import timezone

        sejour = Sejour.objects.create(
            episode=episode, lit=lit, date_admission=timezone.now(), admis_par=utilisateur
        )
        sejour.cloturer(mode_sortie=Sejour.ModeSortie.GUERISON, diagnostic_sortie=diagnostic_cim11)
        lit.refresh_from_db()
        assert lit.statut == Lit.Statut.LIBRE
        assert sejour.date_sortie is not None
