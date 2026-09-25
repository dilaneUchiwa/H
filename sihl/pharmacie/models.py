"""
Module M4 — Pharmacie et stocks (chapitre 3.5.1, Tableau 11).

Règle impérative du mémoire : **Médicament ≠ Lot**. Le stock est porté par
les lots (péremption, quantité), jamais par un compteur global unique sur
le produit. `Medicament.stock_courant` est une dénormalisation (somme des
lots non périmés) maintenue **uniquement** par le trigger PostgreSQL défini
dans `migrations/0002_triggers_denormalisation.py`, déclenché sur
`MouvementStock` — jamais écrite directement par le code applicatif.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class Medicament(models.Model):
    """Catalogue produit (DCI). Le stock n'est jamais géré ici directement."""

    code = models.SlugField(max_length=30, unique=True)
    denomination_commune = models.CharField(max_length=200, help_text="DCI")
    nom = models.CharField(max_length=200)
    forme = models.CharField(max_length=100, blank=True)
    dosage = models.CharField(max_length=50, blank=True)
    seuil_alerte = models.PositiveIntegerField(default=10)

    # Dénormalisation Tableau 11 : écriture réservée au trigger DB.
    stock_courant = models.IntegerField(default=0, editable=False)

    class Meta:
        verbose_name = "médicament"
        ordering = ["nom"]

    def __str__(self) -> str:
        return f"{self.nom} ({self.dosage})" if self.dosage else self.nom

    def en_alerte_seuil(self) -> bool:
        return self.stock_courant <= self.seuil_alerte


class LotPharmaceutique(models.Model):
    """Stock physique réel : chaque lot porte sa propre quantité et péremption."""

    medicament = models.ForeignKey(Medicament, on_delete=models.PROTECT, related_name="lots")
    numero_lot = models.CharField(max_length=50)
    date_peremption = models.DateField(db_index=True)
    quantite_initiale = models.PositiveIntegerField()
    quantite_restante = models.IntegerField()
    fournisseur = models.CharField(max_length=200, blank=True)
    recu_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "lot pharmaceutique"
        unique_together = ("medicament", "numero_lot")
        ordering = ["date_peremption"]

    def __str__(self) -> str:
        return f"{self.medicament} — lot {self.numero_lot}"

    def perime(self) -> bool:
        from django.utils import timezone

        return self.date_peremption < timezone.now().date()


class MouvementStock(models.Model):
    class TypeMouvement(models.TextChoices):
        ENTREE = "ENTREE", "Entrée"
        SORTIE = "SORTIE", "Sortie (dispensation)"
        AJUSTEMENT = "AJUSTEMENT", "Ajustement d'inventaire"
        PEREMPTION = "PEREMPTION", "Retrait pour péremption"

    lot = models.ForeignKey(LotPharmaceutique, on_delete=models.PROTECT, related_name="mouvements")
    type_mouvement = models.CharField(max_length=15, choices=TypeMouvement.choices)
    quantite = models.IntegerField(help_text="Positif en entrée, négatif en sortie.")
    date = models.DateTimeField(auto_now_add=True)
    ligne_prescription = models.ForeignKey(
        "prescriptions.LignePrescription", null=True, blank=True, on_delete=models.SET_NULL
    )
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    motif = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "mouvement de stock"
        indexes = [models.Index(fields=["lot", "date"], name="idx_mouvement_lot_date")]
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.get_type_mouvement_display()} {self.quantite} — {self.lot}"

    def save(self, *args, **kwargs):
        # Le trigger DB maintient Medicament.stock_courant ; ici on ne fait
        # que décrémenter la quantité du lot lui-même (donnée primaire).
        creation = self.pk is None
        super().save(*args, **kwargs)
        if creation:
            LotPharmaceutique.objects.filter(pk=self.lot_id).update(
                quantite_restante=models.F("quantite_restante") + self.quantite
            )
