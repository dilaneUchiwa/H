from django.contrib import admin

from .models import EpisodeDeSoins


@admin.register(EpisodeDeSoins)
class EpisodeDeSoinsAdmin(admin.ModelAdmin):
    list_display = ("numero", "patient", "type_episode", "statut", "montant_du", "montant_paye")
    list_filter = ("statut", "type_episode")
    search_fields = ("numero", "patient__nom", "patient__ipp")
    readonly_fields = ("numero", "montant_du", "montant_paye")
