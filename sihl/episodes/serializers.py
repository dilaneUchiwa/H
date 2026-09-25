from rest_framework import serializers

from .models import EpisodeDeSoins


class EpisodeDeSoinsSerializer(serializers.ModelSerializer):
    solde = serializers.SerializerMethodField()

    class Meta:
        model = EpisodeDeSoins
        fields = [
            "id",
            "numero",
            "patient",
            "type_episode",
            "statut",
            "date_ouverture",
            "date_fermeture",
            "montant_du",
            "montant_paye",
            "solde",
        ]
        read_only_fields = ["id", "numero", "date_ouverture", "montant_du", "montant_paye"]

    def get_solde(self, obj):
        return obj.solde()
