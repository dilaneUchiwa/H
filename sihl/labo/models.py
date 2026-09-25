"""Module M3 — Laboratoire (chapitre 3.5.1)."""

from __future__ import annotations

from django.conf import settings
from django.db import models


class CatalogueExamen(models.Model):
    """Table de paramétrage (nomenclature des examens) — ⚠️ À DÉCIDER #4."""

    code = models.SlugField(max_length=30, unique=True)
    libelle = models.CharField(max_length=200)
    unite = models.CharField(max_length=30, blank=True)
    valeur_reference_min = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    valeur_reference_max = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

    class Meta:
        verbose_name = "examen du catalogue"
        ordering = ["libelle"]

    def __str__(self) -> str:
        return self.libelle


class ExamenLabo(models.Model):
    class Statut(models.TextChoices):
        PRESCRIT = "PRESCRIT", "Prescrit"
        PRELEVE = "PRELEVE", "Prélevé"
        VALIDE = "VALIDE", "Validé"

    ligne_prescription = models.OneToOneField(
        "prescriptions.LignePrescription", on_delete=models.CASCADE, related_name="examen_labo"
    )
    catalogue = models.ForeignKey(CatalogueExamen, on_delete=models.PROTECT)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.PRESCRIT)
    demande_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "examen de laboratoire"
        indexes = [models.Index(fields=["statut"], name="idx_examen_statut")]

    def __str__(self) -> str:
        return f"{self.catalogue} — {self.get_statut_display()}"


class ResultatExamen(models.Model):
    examen = models.OneToOneField(ExamenLabo, on_delete=models.CASCADE, related_name="resultat")
    valeur = models.CharField(max_length=100)
    unite = models.CharField(max_length=30, blank=True)
    hors_reference = models.BooleanField(default=False)
    critique = models.BooleanField(
        default=False, help_text="Déclenche l'alerte valeur critique (Should)."
    )
    valide_le = models.DateTimeField(auto_now_add=True)
    valide_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "résultat d'examen"

    def __str__(self) -> str:
        return f"{self.examen} = {self.valeur} {self.unite}"

    def save(self, *args, **kwargs):
        cat = self.examen.catalogue
        try:
            valeur_numerique = float(self.valeur)
            if cat.valeur_reference_min is not None and valeur_numerique < float(cat.valeur_reference_min):
                self.hors_reference = True
            if cat.valeur_reference_max is not None and valeur_numerique > float(cat.valeur_reference_max):
                self.hors_reference = True
        except ValueError:
            pass
        super().save(*args, **kwargs)
        self.examen.statut = ExamenLabo.Statut.VALIDE
        self.examen.save(update_fields=["statut"])
