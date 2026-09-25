from django.contrib import admin

from .models import LotPharmaceutique, Medicament, MouvementStock


@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    list_display = ("nom", "dosage", "stock_courant", "seuil_alerte")
    search_fields = ("code", "nom", "denomination_commune")
    readonly_fields = ("stock_courant",)


@admin.register(LotPharmaceutique)
class LotPharmaceutiqueAdmin(admin.ModelAdmin):
    list_display = ("medicament", "numero_lot", "date_peremption", "quantite_restante")
    list_filter = ("date_peremption",)
    readonly_fields = ("quantite_restante",)


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ("lot", "type_mouvement", "quantite", "date")
    list_filter = ("type_mouvement",)
