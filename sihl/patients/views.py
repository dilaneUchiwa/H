import datetime

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sihl.core.models import JournalAudit

from . import services
from .models import FusionPatient, Patient
from .serializers import CandidatDoublonSerializer, FusionPatientSerializer, PatientSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    Module M1 : recherche multi-critères sur `nom`, `prenom`, `ipp`,
    `telephone` via ?search=, détection de doublons à la création
    (endpoint `verifier-doublons/`), fusion de fiches (`fusionner/`).
    """

    queryset = Patient.objects.filter(actif=True).order_by("-cree_le")
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["sexe", "actif"]
    search_fields = ["nom", "prenom", "ipp", "telephone"]

    def get_queryset(self):
        queryset = super().get_queryset()
        recherche = self.request.query_params.get("q")
        if recherche:
            queryset = Patient.objects.filter(actif=True).filter(
                models_query_recherche(recherche)
            )
        return queryset

    def perform_create(self, serializer):
        patient = serializer.save(cree_par=self.request.user)
        JournalAudit.enregistrer(
            auteur=self.request.user,
            entite="Patient",
            entite_id=patient.pk,
            action="creation",
            valeurs_apres=PatientSerializer(patient).data,
        )

    def perform_update(self, serializer):
        avant = PatientSerializer(self.get_object()).data
        patient = serializer.save()
        JournalAudit.enregistrer(
            auteur=self.request.user,
            entite="Patient",
            entite_id=patient.pk,
            action="modification",
            valeurs_avant=avant,
            valeurs_apres=PatientSerializer(patient).data,
        )

    @action(detail=False, methods=["get"])
    def verifier_doublons(self, request):
        nom = request.query_params.get("nom", "")
        prenom = request.query_params.get("prenom", "")
        telephone = request.query_params.get("telephone", "")
        date_naissance_str = request.query_params.get("date_naissance")
        date_naissance = None
        if date_naissance_str:
            try:
                date_naissance = datetime.date.fromisoformat(date_naissance_str)
            except ValueError:
                pass

        candidats = services.rechercher_doublons(
            nom=nom, prenom=prenom, date_naissance=date_naissance, telephone=telephone
        )
        return Response(CandidatDoublonSerializer(candidats, many=True).data)

    @action(detail=True, methods=["post"])
    def fusionner(self, request, pk=None):
        absorbe = self.get_object()
        cible_id = request.data.get("patient_cible")
        cible = Patient.objects.get(pk=cible_id)
        fusion = services.fusionner_patients(absorbe=absorbe, cible=cible, auteur=request.user)
        return Response(FusionPatientSerializer(fusion).data, status=201)


class FusionPatientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FusionPatient.objects.all()
    serializer_class = FusionPatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["post"])
    def annuler(self, request, pk=None):
        fusion = self.get_object()
        services.annuler_fusion(fusion, auteur=request.user)
        return Response(FusionPatientSerializer(fusion).data)


def models_query_recherche(terme: str):
    from django.db.models import Q

    return Q(nom__icontains=terme) | Q(prenom__icontains=terme) | Q(ipp__icontains=terme) | Q(
        telephone__icontains=terme
    )
