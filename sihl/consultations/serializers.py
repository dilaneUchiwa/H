from rest_framework import serializers

from .models import Allergie, Consultation, Diagnostic, DiagnosticCIM11


class DiagnosticCIM11Serializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticCIM11
        fields = ["id", "code", "libelle"]


class AllergieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergie
        fields = ["id", "patient", "libelle", "severite", "signalee_le"]
        read_only_fields = ["id", "signalee_le"]


class DiagnosticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnostic
        fields = ["id", "consultation", "code_cim11", "principal", "commentaire"]


class ConsultationSerializer(serializers.ModelSerializer):
    diagnostics = DiagnosticSerializer(many=True, read_only=True)
    allergies_patient = serializers.SerializerMethodField()

    class Meta:
        model = Consultation
        fields = [
            "id",
            "episode",
            "medecin",
            "date",
            "temperature_c",
            "tension_arterielle_systolique",
            "tension_arterielle_diastolique",
            "frequence_cardiaque",
            "frequence_respiratoire",
            "poids_kg",
            "motif",
            "anamnese",
            "examen_clinique",
            "conclusion",
            "modele_utilise",
            "diagnostics",
            "allergies_patient",
        ]
        read_only_fields = ["id", "date", "medecin"]

    def get_allergies_patient(self, obj):
        return AllergieSerializer(obj.episode.patient.allergies.all(), many=True).data
