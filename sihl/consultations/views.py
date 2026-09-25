from rest_framework import permissions, viewsets

from .models import Allergie, Consultation, Diagnostic, DiagnosticCIM11
from .serializers import (
    AllergieSerializer,
    ConsultationSerializer,
    DiagnosticCIM11Serializer,
    DiagnosticSerializer,
)


class DiagnosticCIM11ViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DiagnosticCIM11.objects.all()
    serializer_class = DiagnosticCIM11Serializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["code", "libelle"]


class AllergieViewSet(viewsets.ModelViewSet):
    queryset = Allergie.objects.all()
    serializer_class = AllergieSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["patient"]


class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["episode"]

    def perform_create(self, serializer):
        serializer.save(medecin=self.request.user)


class DiagnosticViewSet(viewsets.ModelViewSet):
    queryset = Diagnostic.objects.all()
    serializer_class = DiagnosticSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["consultation"]
