from django.urls import path

from . import views

urlpatterns = [
    path("rapports/mensuel/", views.rapport_mensuel_district, name="rapport-mensuel"),
    path("rapports/export-dhis2/", views.export_dhis2, name="export-dhis2"),
    path("fhir/Patient/<int:pk>/", views.fhir_patient, name="fhir-patient"),
    path("fhir/Encounter/<int:pk>/", views.fhir_encounter, name="fhir-encounter"),
    path("fhir/Observation/consultation/<int:pk>/", views.fhir_observations, name="fhir-observation"),
]
