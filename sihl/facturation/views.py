from rest_framework import permissions, viewsets

from sihl.core.models import JournalAudit

from .models import ActeFacturable, JournalCaisse, Paiement, TarifActe
from .serializers import (
    ActeFacturableSerializer,
    JournalCaisseSerializer,
    PaiementSerializer,
    TarifActeSerializer,
)


class TarifActeViewSet(viewsets.ModelViewSet):
    queryset = TarifActe.objects.all()
    serializer_class = TarifActeSerializer
    permission_classes = [permissions.IsAuthenticated]


class ActeFacturableViewSet(viewsets.ModelViewSet):
    queryset = ActeFacturable.objects.all()
    serializer_class = ActeFacturableSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["episode"]

    def perform_create(self, serializer):
        acte = serializer.save(facture_par=self.request.user)
        if acte.exoneration:
            JournalAudit.enregistrer(
                auteur=self.request.user,
                entite="ActeFacturable",
                entite_id=acte.pk,
                action="exoneration",
                valeurs_apres={"motif": acte.motif_exoneration, "episode": acte.episode.numero},
            )


class PaiementViewSet(viewsets.ModelViewSet):
    queryset = Paiement.objects.all()
    serializer_class = PaiementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["episode", "mode"]

    def perform_create(self, serializer):
        paiement = serializer.save(encaisse_par=self.request.user)
        JournalAudit.enregistrer(
            auteur=self.request.user,
            entite="Paiement",
            entite_id=paiement.pk,
            action="encaissement",
            valeurs_apres={"montant": str(paiement.montant), "recu": paiement.numero_recu},
        )


class JournalCaisseViewSet(viewsets.ModelViewSet):
    queryset = JournalCaisse.objects.all()
    serializer_class = JournalCaisseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(cloture_par=self.request.user)
