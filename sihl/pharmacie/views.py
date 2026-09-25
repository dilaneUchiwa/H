from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import LotPharmaceutique, Medicament, MouvementStock
from .serializers import LotPharmaceutiqueSerializer, MedicamentSerializer, MouvementStockSerializer


class MedicamentViewSet(viewsets.ModelViewSet):
    queryset = Medicament.objects.all()
    serializer_class = MedicamentSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["code", "nom", "denomination_commune"]

    @action(detail=False, methods=["get"])
    def alertes_seuil(self, request):
        medicaments = [m for m in self.get_queryset() if m.en_alerte_seuil()]
        return Response(MedicamentSerializer(medicaments, many=True).data)


class LotPharmaceutiqueViewSet(viewsets.ModelViewSet):
    queryset = LotPharmaceutique.objects.all()
    serializer_class = LotPharmaceutiqueSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["medicament"]

    @action(detail=False, methods=["get"])
    def alertes_peremption(self, request):
        from datetime import timedelta

        from django.utils import timezone

        horizon = timezone.now().date() + timedelta(days=30)
        lots = self.get_queryset().filter(date_peremption__lte=horizon, quantite_restante__gt=0)
        return Response(LotPharmaceutiqueSerializer(lots, many=True).data)


class MouvementStockViewSet(viewsets.ModelViewSet):
    queryset = MouvementStock.objects.all()
    serializer_class = MouvementStockSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["lot", "type_mouvement"]

    def perform_create(self, serializer):
        serializer.save(utilisateur=self.request.user)
