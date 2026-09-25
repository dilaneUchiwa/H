from rest_framework import serializers

from .models import LotPharmaceutique, Medicament, MouvementStock


class MedicamentSerializer(serializers.ModelSerializer):
    en_alerte = serializers.SerializerMethodField()

    class Meta:
        model = Medicament
        fields = [
            "id",
            "code",
            "denomination_commune",
            "nom",
            "forme",
            "dosage",
            "seuil_alerte",
            "stock_courant",
            "en_alerte",
        ]
        read_only_fields = ["id", "stock_courant"]

    def get_en_alerte(self, obj):
        return obj.en_alerte_seuil()


class LotPharmaceutiqueSerializer(serializers.ModelSerializer):
    perime = serializers.SerializerMethodField()

    class Meta:
        model = LotPharmaceutique
        fields = [
            "id",
            "medicament",
            "numero_lot",
            "date_peremption",
            "quantite_initiale",
            "quantite_restante",
            "fournisseur",
            "recu_le",
            "perime",
        ]
        read_only_fields = ["id", "quantite_restante", "recu_le"]

    def get_perime(self, obj):
        return obj.perime()

    def create(self, validated_data):
        validated_data["quantite_restante"] = 0
        lot = super().create(validated_data)
        MouvementStock.objects.create(
            lot=lot,
            type_mouvement=MouvementStock.TypeMouvement.ENTREE,
            quantite=lot.quantite_initiale,
            utilisateur=self.context["request"].user,
            motif="Réception initiale du lot",
        )
        return lot


class MouvementStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = MouvementStock
        fields = [
            "id",
            "lot",
            "type_mouvement",
            "quantite",
            "date",
            "ligne_prescription",
            "utilisateur",
            "motif",
        ]
        read_only_fields = ["id", "date", "utilisateur"]
