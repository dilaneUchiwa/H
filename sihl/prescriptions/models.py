"""Module M3 — Prescription (DCI) (chapitre 3.5.1)."""

from __future__ import annotations

from django.conf import settings
from django.db import models


class Prescription(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        PARTIELLE = "PARTIELLE", "Partiellement honorée"
        HONOREE = "HONOREE", "Honorée"
        ANNULEE = "ANNULEE", "Annulée"

    consultation = models.ForeignKey(
        "consultations.Consultation", on_delete=models.CASCADE, related_name="prescriptions"
    )
    prescripteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=15, choices=Statut.choices, default=Statut.EN_ATTENTE)

    class Meta:
        verbose_name = "prescription"
        indexes = [
            # Index partiel (Tableau 12) : file d'attente pharmacie/labo restreinte
            # aux prescriptions non honorées.
            models.Index(
                fields=["statut"],
                name="idx_prescription_en_attente",
                condition=models.Q(statut="EN_ATTENTE"),
            ),
        ]
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"Prescription #{self.pk} ({self.consultation})"


class LignePrescription(models.Model):
    class Type(models.TextChoices):
        MEDICAMENT = "MEDICAMENT", "Médicament"
        EXAMEN = "EXAMEN", "Examen de laboratoire"

    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="lignes")
    type_ligne = models.CharField(max_length=15, choices=Type.choices)

    medicament = models.ForeignKey(
        "pharmacie.Medicament", null=True, blank=True, on_delete=models.PROTECT
    )
    examen = models.ForeignKey("labo.CatalogueExamen", null=True, blank=True, on_delete=models.PROTECT)

    # Dénormalisation Tableau 11 : copié à l'écriture, jamais modifié
    # ensuite — préserve l'intégrité historique même si le catalogue change.
    libelle_produit = models.CharField(max_length=200, editable=False)

    posologie = models.CharField(max_length=200, blank=True)
    quantite = models.PositiveIntegerField(default=1)
    honoree = models.BooleanField(default=False)

    class Meta:
        verbose_name = "ligne de prescription"

    def __str__(self) -> str:
        return f"{self.libelle_produit} x{self.quantite}"

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.type_ligne == self.Type.MEDICAMENT and self.medicament_id:
                self.libelle_produit = self.medicament.nom
            elif self.type_ligne == self.Type.EXAMEN and self.examen_id:
                self.libelle_produit = self.examen.libelle
        super().save(*args, **kwargs)
