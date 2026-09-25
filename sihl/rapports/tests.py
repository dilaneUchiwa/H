import datetime

import pytest
from django.utils import timezone

from sihl.consultations.models import Consultation, Diagnostic
from sihl.facturation.models import Paiement

from .agregation import rapport_mensuel
from .export import export_csv_dhis2
from .fhir import episode_vers_encounter, patient_vers_fhir


@pytest.mark.django_db
class TestAgregation:
    def test_rapport_compte_les_consultations_du_mois(self, episode, utilisateur, diagnostic_cim11):
        consultation = Consultation.objects.create(episode=episode, medecin=utilisateur, motif="Test")
        Diagnostic.objects.create(consultation=consultation, code_cim11=diagnostic_cim11)
        Paiement.objects.create(episode=episode, montant=1000, encaisse_par=utilisateur)

        aujourdhui = timezone.now()
        rapport = rapport_mensuel(aujourdhui.year, aujourdhui.month)

        assert rapport["nombre_consultations"] == 1
        assert rapport["recettes_totales"] == 1000
        assert rapport["diagnostics_frequents"][0]["nombre"] == 1

    def test_rapport_mois_vide(self):
        rapport = rapport_mensuel(2020, 1)
        assert rapport["nombre_consultations"] == 0
        assert rapport["recettes_totales"] == 0


@pytest.mark.django_db
class TestExportDHIS2:
    def test_export_csv_contient_les_indicateurs(self, episode, utilisateur):
        Paiement.objects.create(episode=episode, montant=500, encaisse_par=utilisateur)
        aujourdhui = timezone.now()
        contenu = export_csv_dhis2(aujourdhui.year, aujourdhui.month)
        assert "recettes_totales" in contenu
        assert "500" in contenu


@pytest.mark.django_db
class TestProjectionFHIR:
    def test_patient_vers_fhir(self, patient):
        ressource = patient_vers_fhir(patient)
        assert ressource["resourceType"] == "Patient"
        assert ressource["identifier"][0]["value"] == patient.ipp
        assert ressource["gender"] == "female"

    def test_episode_vers_encounter(self, episode):
        ressource = episode_vers_encounter(episode)
        assert ressource["resourceType"] == "Encounter"
        assert ressource["subject"]["reference"] == f"Patient/{episode.patient_id}"
