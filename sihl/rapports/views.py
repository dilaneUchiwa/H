from django.http import HttpResponse
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from sihl.consultations.models import Consultation
from sihl.episodes.models import EpisodeDeSoins
from sihl.patients.models import Patient

from . import fhir
from .agregation import rapport_mensuel
from .export import export_csv_dhis2


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def rapport_mensuel_district(request):
    annee = int(request.query_params.get("annee"))
    mois = int(request.query_params.get("mois"))
    return Response(rapport_mensuel(annee, mois))


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def export_dhis2(request):
    annee = int(request.query_params.get("annee"))
    mois = int(request.query_params.get("mois"))
    contenu = export_csv_dhis2(annee, mois)
    reponse = HttpResponse(contenu, content_type="text/csv")
    reponse["Content-Disposition"] = f'attachment; filename="dhis2_{annee}_{mois:02d}.csv"'
    return reponse


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def fhir_patient(request, pk):
    patient = Patient.objects.get(pk=pk)
    return Response(fhir.patient_vers_fhir(patient))


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def fhir_encounter(request, pk):
    episode = EpisodeDeSoins.objects.get(pk=pk)
    return Response(fhir.episode_vers_encounter(episode))


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def fhir_observations(request, pk):
    consultation = Consultation.objects.get(pk=pk)
    return Response(fhir.consultation_vers_observations(consultation))
