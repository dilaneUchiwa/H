from rest_framework import permissions, viewsets

from .models import LignePrescription, Prescription
from .serializers import LignePrescriptionSerializer, PrescriptionSerializer


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["consultation", "statut"]

    def perform_create(self, serializer):
        serializer.save(prescripteur=self.request.user)


class LignePrescriptionViewSet(viewsets.ModelViewSet):
    queryset = LignePrescription.objects.all()
    serializer_class = LignePrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["prescription", "type_ligne", "honoree"]
