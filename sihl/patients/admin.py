from django.contrib import admin

from .models import CorrespondanceGraphie, FusionPatient, Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("ipp", "nom", "prenom", "date_naissance", "telephone", "actif")
    search_fields = ("ipp", "nom", "prenom", "telephone")
    list_filter = ("actif", "sexe")
    readonly_fields = ("ipp", "cle_phonetique", "annee_creation")


@admin.register(CorrespondanceGraphie)
class CorrespondanceGraphieAdmin(admin.ModelAdmin):
    list_display = ("graphie", "graphie_canonique")
    search_fields = ("graphie", "graphie_canonique")


@admin.register(FusionPatient)
class FusionPatientAdmin(admin.ModelAdmin):
    list_display = ("patient_absorbe", "patient_cible", "effectuee_le", "annulee")
