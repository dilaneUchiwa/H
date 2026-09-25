from django.contrib import admin

from .models import CatalogueExamen, ExamenLabo, ResultatExamen


@admin.register(CatalogueExamen)
class CatalogueExamenAdmin(admin.ModelAdmin):
    list_display = ("code", "libelle", "unite", "valeur_reference_min", "valeur_reference_max")
    search_fields = ("code", "libelle")


@admin.register(ExamenLabo)
class ExamenLaboAdmin(admin.ModelAdmin):
    list_display = ("catalogue", "statut", "demande_le")
    list_filter = ("statut",)


@admin.register(ResultatExamen)
class ResultatExamenAdmin(admin.ModelAdmin):
    list_display = ("examen", "valeur", "unite", "hors_reference", "critique")
