import pytest
from django.core.management import call_command

from .models import Utilisateur


@pytest.mark.django_db
class TestAssurerSuperutilisateur:
    def test_cree_le_compte_si_absent(self, monkeypatch):
        monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "admin-init")
        monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "motdepasse-robuste-1")
        monkeypatch.setenv("DJANGO_SUPERUSER_EMAIL", "admin@example.org")

        call_command("assurer_superutilisateur")

        utilisateur = Utilisateur.objects.get(username="admin-init")
        assert utilisateur.is_superuser is True
        assert utilisateur.is_staff is True
        assert utilisateur.check_password("motdepasse-robuste-1")

    def test_idempotent_met_a_jour_le_mot_de_passe(self, monkeypatch):
        monkeypatch.setenv("DJANGO_SUPERUSER_USERNAME", "admin-init")
        monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "premier-mdp-robuste")
        call_command("assurer_superutilisateur")

        monkeypatch.setenv("DJANGO_SUPERUSER_PASSWORD", "second-mdp-robuste")
        call_command("assurer_superutilisateur")

        assert Utilisateur.objects.filter(username="admin-init").count() == 1
        utilisateur = Utilisateur.objects.get(username="admin-init")
        assert utilisateur.check_password("second-mdp-robuste")

    def test_ne_fait_rien_sans_variables(self, monkeypatch):
        monkeypatch.delenv("DJANGO_SUPERUSER_USERNAME", raising=False)
        monkeypatch.delenv("DJANGO_SUPERUSER_PASSWORD", raising=False)
        call_command("assurer_superutilisateur")
        assert Utilisateur.objects.count() == 0
