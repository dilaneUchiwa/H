"""Fixtures pytest partagées par toutes les apps (tests unitaires + API)."""

import datetime

import pytest
from rest_framework.test import APIClient

from sihl.consultations.models import Consultation, DiagnosticCIM11
from sihl.core.models import Utilisateur
from sihl.episodes.models import EpisodeDeSoins
from sihl.facturation.models import TarifActe
from sihl.hospitalisation.models import Lit, Service
from sihl.labo.models import CatalogueExamen
from sihl.patients.models import Patient
from sihl.pharmacie.models import LotPharmaceutique, Medicament
from sihl.prescriptions.models import Prescription


@pytest.fixture
def utilisateur(db):
    return Utilisateur.objects.create_user(username="agent", password="motdepasse-robuste-1")


@pytest.fixture
def superutilisateur(db):
    return Utilisateur.objects.create_superuser(
        username="admin", password="motdepasse-robuste-1", email="admin@example.org"
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def client_authentifie(api_client, superutilisateur):
    """
    Client authentifié avec un compte superutilisateur : contourne
    volontairement les restrictions fines de RBAC pour se concentrer, dans
    ces tests, sur le comportement métier de chaque endpoint.
    """
    api_client.force_authenticate(user=superutilisateur)
    return api_client


@pytest.fixture
def patient(db, utilisateur):
    return Patient.objects.create(
        nom="Ngoma", prenom="Awa", sexe="F",
        date_naissance=datetime.date(1990, 5, 12), telephone="699000001",
        cree_par=utilisateur,
    )


@pytest.fixture
def episode(db, patient, utilisateur):
    return EpisodeDeSoins.objects.create(patient=patient, ouvert_par=utilisateur)


@pytest.fixture
def service_hospitalier(db):
    return Service.objects.create(code="med-int", nom="Médecine interne")


@pytest.fixture
def lit(db, service_hospitalier):
    return Lit.objects.create(service=service_hospitalier, numero="01")


@pytest.fixture
def consultation(db, episode, utilisateur):
    return Consultation.objects.create(episode=episode, medecin=utilisateur, motif="Motif de test")


@pytest.fixture
def diagnostic_cim11(db):
    return DiagnosticCIM11.objects.create(code="1A00", libelle="Choléra")


@pytest.fixture
def catalogue_examen(db):
    return CatalogueExamen.objects.create(
        code="glycemie", libelle="Glycémie à jeun", unite="g/L",
        valeur_reference_min=0.7, valeur_reference_max=1.1,
    )


@pytest.fixture
def tarif_acte(db):
    return TarifActe.objects.create(code="consult-gen", libelle="Consultation générale", montant=2000)


@pytest.fixture
def medicament(db):
    return Medicament.objects.create(
        code="paracetamol-500", nom="Paracétamol", dosage="500mg", seuil_alerte=20
    )


@pytest.fixture
def prescription(db, consultation, utilisateur):
    return Prescription.objects.create(consultation=consultation, prescripteur=utilisateur)


@pytest.fixture
def lot_pharmaceutique(db, medicament):
    return LotPharmaceutique.objects.create(
        medicament=medicament,
        numero_lot="L2026-001",
        date_peremption=datetime.date.today() + datetime.timedelta(days=365),
        quantite_initiale=100,
        quantite_restante=100,
    )
