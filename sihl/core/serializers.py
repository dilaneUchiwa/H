from rest_framework import serializers

from .models import JournalAudit, Role, Utilisateur


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "code", "libelle", "acces_contenu_clinique"]


class UtilisateurSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)

    class Meta:
        model = Utilisateur
        fields = ["id", "username", "first_name", "last_name", "telephone", "roles", "is_active"]


class JournalAuditSerializer(serializers.ModelSerializer):
    auteur = serializers.StringRelatedField()

    class Meta:
        model = JournalAudit
        fields = [
            "id",
            "horodatage",
            "auteur",
            "entite",
            "entite_id",
            "action",
            "valeurs_avant",
            "valeurs_apres",
        ]
        read_only_fields = fields
