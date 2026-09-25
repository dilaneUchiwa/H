from rest_framework import permissions, viewsets

from .models import CatalogueExamen, ExamenLabo, ResultatExamen
from .serializers import CatalogueExamenSerializer, ExamenLaboSerializer, ResultatExamenSerializer


class CatalogueExamenViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CatalogueExamen.objects.all()
    serializer_class = CatalogueExamenSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExamenLaboViewSet(viewsets.ModelViewSet):
    queryset = ExamenLabo.objects.all()
    serializer_class = ExamenLaboSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["statut", "catalogue"]


class ResultatExamenViewSet(viewsets.ModelViewSet):
    queryset = ResultatExamen.objects.all()
    serializer_class = ResultatExamenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(valide_par=self.request.user)
