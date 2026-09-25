from rest_framework import serializers

from .models import LignePrescription, Prescription


class LignePrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LignePrescription
        fields = [
            "id",
            "prescription",
            "type_ligne",
            "medicament",
            "examen",
            "libelle_produit",
            "posologie",
            "quantite",
            "honoree",
        ]
        read_only_fields = ["id", "libelle_produit"]


class PrescriptionSerializer(serializers.ModelSerializer):
    lignes = LignePrescriptionSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = ["id", "consultation", "prescripteur", "date", "statut", "lignes"]
        read_only_fields = ["id", "date", "prescripteur"]
