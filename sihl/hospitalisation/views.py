from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Lit, Service, Sejour, SoinQuotidien
from .serializers import LitSerializer, SejourSerializer, ServiceSerializer, SoinQuotidienSerializer


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]


class LitViewSet(viewsets.ModelViewSet):
    queryset = Lit.objects.all()
    serializer_class = LitSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["service", "statut"]


class SejourViewSet(viewsets.ModelViewSet):
    """Plan des lits temps réel via ?statut du lit ; admission/sortie (M6)."""

    queryset = Sejour.objects.all()
    serializer_class = SejourSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["lit__service", "mode_sortie"]

    def perform_create(self, serializer):
        serializer.save(admis_par=self.request.user)

    @action(detail=True, methods=["post"])
    def sortie(self, request, pk=None):
        from sihl.consultations.models import DiagnosticCIM11

        sejour = self.get_object()
        diagnostic_id = request.data.get("diagnostic_sortie")
        diagnostic = DiagnosticCIM11.objects.filter(pk=diagnostic_id).first() if diagnostic_id else None
        sejour.cloturer(mode_sortie=request.data.get("mode_sortie"), diagnostic_sortie=diagnostic)
        return Response(SejourSerializer(sejour).data)


class SoinQuotidienViewSet(viewsets.ModelViewSet):
    queryset = SoinQuotidien.objects.all()
    serializer_class = SoinQuotidienSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["sejour"]

    def perform_create(self, serializer):
        serializer.save(realise_par=self.request.user)
