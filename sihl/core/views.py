from rest_framework import mixins, permissions, viewsets
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
