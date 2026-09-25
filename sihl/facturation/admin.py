from django.contrib import admin

from .models import ActeFacturable, JournalCaisse, Paiement, TarifActe


@admin.register(TarifActe)
class TarifActeAdmin(admin.ModelAdmin):
    list_display = ("code", "libelle", "montant", "actif")


@admin.register(ActeFacturable)
class ActeFacturableAdmin(admin.ModelAdmin):
    list_display = ("episode", "tarif", "quantite", "montant", "exoneration")
    readonly_fields = ("montant",)


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ("numero_recu", "episode", "montant", "mode", "date", "encaisse_par")
    readonly_fields = ("numero_recu",)


@admin.register(JournalCaisse)
class JournalCaisseAdmin(admin.ModelAdmin):
    list_display = ("date_cloture", "montant_theorique", "montant_compte", "ecart")
    readonly_fields = ("ecart",)
