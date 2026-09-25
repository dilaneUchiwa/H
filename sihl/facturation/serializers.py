from rest_framework import serializers

from .models import ActeFacturable, JournalCaisse, Paiement, TarifActe


class TarifActeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TarifActe
        fields = ["id", "code", "libelle", "montant", "actif"]


class ActeFacturableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActeFacturable
        fields = [
            "id",
            "episode",
            "tarif",
            "quantite",
            "montant",
            "exoneration",
            "motif_exoneration",
            "facture_le",
            "facture_par",
        ]
        read_only_fields = ["id", "montant", "facture_le", "facture_par"]


class PaiementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paiement
        fields = ["id", "episode", "montant", "mode", "numero_recu", "date", "encaisse_par"]
        read_only_fields = ["id", "numero_recu", "date", "encaisse_par"]


class JournalCaisseSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalCaisse
        fields = [
            "id",
            "date_cloture",
            "montant_theorique",
            "montant_compte",
            "ecart",
            "cloture_par",
            "cloture_le",
        ]
        read_only_fields = ["id", "ecart", "cloture_par", "cloture_le"]
