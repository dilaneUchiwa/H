from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sihl.pharmacie.models import LotPharmaceutique
from sihl.pharmacie.services import DispensationImpossible, dispenser

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

    @action(detail=True, methods=["post"])
    def dispenser(self, request, pk=None):
        """Décrémente le lot choisi et marque la ligne honorée (M4)."""
        ligne = self.get_object()
        lot_id = request.data.get("lot")
        quantite = int(request.data.get("quantite", ligne.quantite))
        try:
            lot = LotPharmaceutique.objects.get(pk=lot_id)
        except LotPharmaceutique.DoesNotExist:
            return Response({"detail": "Lot introuvable."}, status=404)

        try:
            dispenser(ligne=ligne, lot=lot, quantite=quantite, utilisateur=request.user)
        except DispensationImpossible as erreur:
            return Response({"detail": str(erreur)}, status=400)

        return Response(LignePrescriptionSerializer(ligne).data)
