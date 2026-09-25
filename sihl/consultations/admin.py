from django.contrib import admin

from .models import Allergie, Consultation, Diagnostic, DiagnosticCIM11


@admin.register(DiagnosticCIM11)
class DiagnosticCIM11Admin(admin.ModelAdmin):
    list_display = ("code", "libelle")
    search_fields = ("code", "libelle")


@admin.register(Allergie)
class AllergieAdmin(admin.ModelAdmin):
    list_display = ("patient", "libelle", "severite")


class DiagnosticInline(admin.TabularInline):
    model = Diagnostic
    extra = 1


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ("episode", "medecin", "date", "motif")
    inlines = [DiagnosticInline]
