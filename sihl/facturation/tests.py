import pytest

from .models import ActeFacturable, JournalCaisse, Paiement


@pytest.mark.django_db
class TestActeFacturableModel:
    def test_montant_calcule_a_l_ecriture(self, episode, tarif_acte):
        acte = ActeFacturable.objects.create(episode=episode, tarif=tarif_acte, quantite=3)
        assert acte.montant == tarif_acte.montant * 3

    def test_exoneration_montant_nul(self, episode, tarif_acte):
        acte = ActeFacturable.objects.create(
            episode=episode, tarif=tarif_acte, quantite=1, exoneration=True, motif_exoneration="Indigent"
        )
        assert acte.montant == 0


@pytest.mark.django_db
class TestPaiementModel:
    def test_numero_recu_genere_et_unique(self, episode, utilisateur):
        p1 = Paiement.objects.create(episode=episode, montant=1000, encaisse_par=utilisateur)
        p2 = Paiement.objects.create(episode=episode, montant=500, encaisse_par=utilisateur)
        assert p1.numero_recu != p2.numero_recu
        assert p1.numero_recu.startswith("RECU-")


@pytest.mark.django_db
class TestJournalCaisseModel:
    def test_ecart_calcule(self, utilisateur):
        journal = JournalCaisse.objects.create(
            date_cloture="2026-01-01", montant_theorique=10000, montant_compte=9500, cloture_par=utilisateur
        )
        assert journal.ecart == -500
