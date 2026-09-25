"""
Crée (ou met à jour) un compte administrateur initial à partir de variables
d'environnement — nécessaire quand la plateforme d'hébergement ne fournit
pas d'accès shell interactif (ex. plan gratuit Render, pas de terminal).

Idempotent : peut tourner à chaque démarrage sans effet de bord une fois le
compte créé, sauf pour la resynchronisation du mot de passe si la variable
d'environnement change (utile pour une rotation de mot de passe via une
simple mise à jour d'environnement, sans shell).
"""

from django.core.management.base import BaseCommand

from sihl.core.models import Utilisateur


class Command(BaseCommand):
    help = "Crée ou met à jour le superutilisateur initial depuis les variables d'environnement."

    def handle(self, *args, **options):
        import os

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

        if not username or not password:
            self.stdout.write(
                "DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD absents : "
                "aucun compte administrateur créé."
            )
            return

        utilisateur, cree = Utilisateur.objects.get_or_create(
            username=username, defaults={"email": email, "is_staff": True, "is_superuser": True}
        )
        utilisateur.email = email
        utilisateur.is_staff = True
        utilisateur.is_superuser = True
        utilisateur.set_password(password)
        utilisateur.save()

        action = "créé" if cree else "mis à jour"
        self.stdout.write(self.style.SUCCESS(f"Superutilisateur '{username}' {action}."))
