import pytest

from .models import JournalAudit, Utilisateur


@pytest.mark.django_db
class TestJournalAudit:
    def test_ecriture_seule_pas_de_modification(self):
        utilisateur = Utilisateur.objects.create_user(username="agent1", password="motdepasse-robuste")
        entree = JournalAudit.enregistrer(
            auteur=utilisateur, entite="Patient", entite_id=1, action="creation"
        )
        entree.action = "modification"
        with pytest.raises(ValueError):
            entree.save()

    def test_pas_de_suppression(self):
        utilisateur = Utilisateur.objects.create_user(username="agent2", password="motdepasse-robuste")
        entree = JournalAudit.enregistrer(
            auteur=utilisateur, entite="Patient", entite_id=1, action="creation"
        )
        with pytest.raises(ValueError):
            entree.delete()
