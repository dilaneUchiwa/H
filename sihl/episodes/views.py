from rest_framework import permissions, viewsets

from .models import EpisodeDeSoins
from .serializers import EpisodeDeSoinsSerializer


class EpisodeDeSoinsViewSet(viewsets.ModelViewSet):
    queryset = EpisodeDeSoins.objects.all()
    serializer_class = EpisodeDeSoinsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["patient", "statut", "type_episode"]

    def perform_create(self, serializer):
        serializer.save(ouvert_par=self.request.user)
