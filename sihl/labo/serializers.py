from rest_framework import serializers

from .models import CatalogueExamen, ExamenLabo, ResultatExamen


class CatalogueExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogueExamen
        fields = ["id", "code", "libelle", "unite", "valeur_reference_min", "valeur_reference_max"]


class ResultatExamenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultatExamen
        fields = ["id", "examen", "valeur", "unite", "hors_reference", "critique", "valide_le", "valide_par"]
        read_only_fields = ["id", "hors_reference", "valide_le", "valide_par"]


class ExamenLaboSerializer(serializers.ModelSerializer):
    resultat = ResultatExamenSerializer(read_only=True)

    class Meta:
        model = ExamenLabo
        fields = ["id", "ligne_prescription", "catalogue", "statut", "demande_le", "resultat"]
        read_only_fields = ["id", "demande_le"]
