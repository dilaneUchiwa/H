"""Module M6 — Hospitalisation (chapitre 3.5.1) + table de paramétrage Service."""

from __future__ import annotations

from django.conf import settings
from django.db import models


class Service(models.Model):
    """Table de paramétrage (⚠️ À DÉCIDER #4 : schéma non détaillé dans le mémoire)."""

    code = models.SlugField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "service"
        ordering = ["nom"]

    def __str__(self) -> str:
        return self.nom


class Lit(models.Model):
    class Statut(models.TextChoices):
        LIBRE = "LIBRE", "Libre"
        OCCUPE = "OCCUPE", "Occupé"
        HORS_SERVICE = "HORS_SERVICE", "Hors service"

    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="lits")
    numero = models.CharField(max_length=20)
    statut = models.CharField(max_length=15, choices=Statut.choices, default=Statut.LIBRE)

    class Meta:
        verbose_name = "lit"
        unique_together = ("service", "numero")
        ordering = ["service", "numero"]

    def __str__(self) -> str:
        return f"{self.service.code}-{self.numero}"


class Sejour(models.Model):
    class ModeSortie(models.TextChoices):
        GUERISON = "GUERISON", "Guérison"
        MUTATION = "MUTATION", "Mutation"
        EVASION = "EVASION", "Évasion"
        DECES = "DECES", "Décès"
        SORTIE_CONTRE_AVIS = "SCAM", "Sortie contre avis médical"
        TRANSFERT = "TRANSFERT", "Transfert"

    episode = models.OneToOneField("episodes.EpisodeDeSoins", on_delete=models.CASCADE, related_name="sejour")
    lit = models.ForeignKey(Lit, on_delete=models.PROTECT, related_name="sejours")
    date_admission = models.DateTimeField()
    date_sortie = models.DateTimeField(null=True, blank=True)
    mode_sortie = models.CharField(max_length=15, choices=ModeSortie.choices, blank=True)
    diagnostic_sortie = models.ForeignKey(
        "consultations.DiagnosticCIM11", null=True, blank=True, on_delete=models.SET_NULL
    )
    admis_par = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "séjour"
        ordering = ["-date_admission"]

    def __str__(self) -> str:
        return f"Séjour {self.episode.numero} — lit {self.lit}"

    def save(self, *args, **kwargs):
        creation = self.pk is None
        super().save(*args, **kwargs)
        if creation:
            self.lit.statut = Lit.Statut.OCCUPE
            self.lit.save(update_fields=["statut"])

    def cloturer(self, *, mode_sortie: str, diagnostic_sortie=None):
        from django.utils import timezone

        self.date_sortie = timezone.now()
        self.mode_sortie = mode_sortie
        self.diagnostic_sortie = diagnostic_sortie
        self.save(update_fields=["date_sortie", "mode_sortie", "diagnostic_sortie"])
        self.lit.statut = Lit.Statut.LIBRE
        self.lit.save(update_fields=["statut"])


class SoinQuotidien(models.Model):
    """Prescriptions/soins quotidiens du séjour (M6)."""

    sejour = models.ForeignKey(Sejour, on_delete=models.CASCADE, related_name="soins")
    date_heure = models.DateTimeField()
    description = models.TextField()
    realise_par = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "soin quotidien"
        ordering = ["-date_heure"]
