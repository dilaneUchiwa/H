import pytest

from .models import EpisodeDeSoins


@pytest.mark.django_db
class TestEpisodeDeSoinsModel:
    def test_numero_genere_automatiquement(self, patient):
        episode = EpisodeDeSoins.objects.create(patient=patient)
        assert episode.numero.startswith("EP-")

    def test_numeros_uniques_et_sequentiels(self, patient):
        e1 = EpisodeDeSoins.objects.create(patient=patient)
        e2 = EpisodeDeSoins.objects.create(patient=patient)
        assert e1.numero != e2.numero

    def test_solde_sans_facturation(self, episode):
        assert episode.solde() == 0
