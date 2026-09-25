from rest_framework import serializers

from .models import FusionPatient, Patient


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "id",
            "ipp",
            "nom",
            "prenom",
            "date_naissance",
            "date_naissance_estimee",
            "sexe",
            "telephone",
            "adresse",
            "actif",
            "cree_le",
        ]
        read_only_fields = ["id", "ipp", "actif", "cree_le"]


class CandidatDoublonSerializer(serializers.Serializer):
    patient = PatientSerializer()
    score = serializers.FloatField()
    details = serializers.DictField(child=serializers.FloatField())


class FusionPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = FusionPatient
        fields = ["id", "patient_absorbe", "patient_cible", "auteur", "effectuee_le", "annulee"]
        read_only_fields = fields
