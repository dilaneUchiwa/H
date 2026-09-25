from django.contrib import admin

from .models import LignePrescription, Prescription


class LignePrescriptionInline(admin.TabularInline):
    model = LignePrescription
    extra = 1
    readonly_fields = ("libelle_produit",)


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "consultation", "prescripteur", "date", "statut")
    list_filter = ("statut",)
    inlines = [LignePrescriptionInline]
