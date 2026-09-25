from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import JournalAudit, ParametreEtablissement, Permission, Role, Utilisateur


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("SIHL", {"fields": ("roles", "telephone", "service_rattachement")}),
    )
    list_display = ("username", "first_name", "last_name", "is_active", "is_staff")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "libelle", "acces_contenu_clinique")
    filter_horizontal = ("permissions",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("code", "libelle")


@admin.register(ParametreEtablissement)
class ParametreEtablissementAdmin(admin.ModelAdmin):
    list_display = ("nom_etablissement", "code_etablissement", "fusion_reversibilite_jours")


@admin.register(JournalAudit)
class JournalAuditAdmin(admin.ModelAdmin):
    list_display = ("horodatage", "auteur", "action", "entite", "entite_id")
    list_filter = ("entite", "action")
    search_fields = ("entite_id",)
    readonly_fields = [f.name for f in JournalAudit._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
