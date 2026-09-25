from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import JournalAudit, Role, Utilisateur
from .serializers import JournalAuditSerializer, RoleSerializer, UtilisateurSerializer


class EstAdministrateur(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class UtilisateurViewSet(viewsets.ModelViewSet):
    queryset = Utilisateur.objects.all().order_by("username")
    serializer_class = UtilisateurSerializer
    permission_classes = [EstAdministrateur]


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [EstAdministrateur]


class JournalAuditViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Lecture seule : la trace ne se modifie jamais depuis l'API."""

    queryset = JournalAudit.objects.all()
    serializer_class = JournalAuditSerializer
    permission_classes = [EstAdministrateur]
    filterset_fields = ["entite", "entite_id", "action"]


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def moi(request):
    return Response(UtilisateurSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def connexion(request):
    """
    Authentification nominative avec verrouillage après échecs répétés
    (chapitre 3.9). Comptes partagés proscrits : un seul `username` par
    session, aucune notion de compte générique n'est exposée ici.
    """
    username = request.data.get("username", "")
    mot_de_passe = request.data.get("password", "")

    try:
        utilisateur = Utilisateur.objects.get(username=username)
    except Utilisateur.DoesNotExist:
        return Response({"detail": "Identifiants invalides."}, status=status.HTTP_401_UNAUTHORIZED)

    if utilisateur.verrouille_jusqu_a and utilisateur.verrouille_jusqu_a > timezone.now():
        return Response(
            {"detail": "Compte verrouillé suite à des échecs répétés. Réessayez plus tard."},
            status=status.HTTP_423_LOCKED,
        )

    utilisateur_authentifie = authenticate(request, username=username, password=mot_de_passe)

    if utilisateur_authentifie is None:
        utilisateur.echecs_authentification += 1
        if utilisateur.echecs_authentification >= settings.MAX_ECHECS_AUTHENTIFICATION:
            from datetime import timedelta

            utilisateur.verrouille_jusqu_a = timezone.now() + timedelta(
                minutes=settings.DUREE_VERROUILLAGE_MINUTES
            )
        utilisateur.save(update_fields=["echecs_authentification", "verrouille_jusqu_a"])
        return Response({"detail": "Identifiants invalides."}, status=status.HTTP_401_UNAUTHORIZED)

    utilisateur.echecs_authentification = 0
    utilisateur.verrouille_jusqu_a = None
    utilisateur.save(update_fields=["echecs_authentification", "verrouille_jusqu_a"])

    login(request, utilisateur_authentifie)
    return Response(UtilisateurSerializer(utilisateur_authentifie).data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def deconnexion(request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)
