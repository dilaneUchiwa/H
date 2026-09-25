from django.contrib import admin

from .models import Lit, Service, Sejour, SoinQuotidien


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "actif")


@admin.register(Lit)
class LitAdmin(admin.ModelAdmin):
    list_display = ("service", "numero", "statut")
    list_filter = ("service", "statut")


class SoinQuotidienInline(admin.TabularInline):
    model = SoinQuotidien
    extra = 0


@admin.register(Sejour)
class SejourAdmin(admin.ModelAdmin):
    list_display = ("episode", "lit", "date_admission", "date_sortie", "mode_sortie")
    inlines = [SoinQuotidienInline]
