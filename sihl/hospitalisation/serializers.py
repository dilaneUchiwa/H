from rest_framework import serializers

from .models import Lit, Service, SoinQuotidien, Sejour


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "code", "nom", "actif"]


class LitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lit
        fields = ["id", "service", "numero", "statut"]
        read_only_fields = ["id", "statut"]


class SoinQuotidienSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoinQuotidien
        fields = ["id", "sejour", "date_heure", "description", "realise_par"]
        read_only_fields = ["id", "realise_par"]


class SejourSerializer(serializers.ModelSerializer):
    soins = SoinQuotidienSerializer(many=True, read_only=True)

    class Meta:
        model = Sejour
        fields = [
            "id",
            "episode",
            "lit",
            "date_admission",
            "date_sortie",
            "mode_sortie",
            "diagnostic_sortie",
            "admis_par",
            "soins",
        ]
        read_only_fields = ["id", "date_sortie", "admis_par"]
