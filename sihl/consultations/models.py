"""Module M2 — Consultation (chapitre 3.5.1)."""

from __future__ import annotations

from django.conf import settings
from django.db import models


class DiagnosticCIM11(models.Model):
    """
    Nomenclature CIM-11 — sous-ensemble local (⚠️ À DÉCIDER #5, DECISIONS.md) :
    table à peupler par import CSV, sans dépendance à une API externe
    (principe d'autonomie).
    """

    code = models.CharField(max_length=10, unique=True)
    libelle = models.CharField(max_length=255)

    class Meta:
        verbose_name = "diagnostic CIM-11"
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} — {self.libelle}"


class Allergie(models.Model):
    """Allergies du patient — doivent rester visibles dans tout le dossier (M2)."""

    class Severite(models.TextChoices):
        LEGERE = "LEGERE", "Légère"
        MODEREE = "MODEREE", "Modérée"
        SEVERE = "SEVERE", "Sévère"

    patient = models.ForeignKey("patients.Patient", on_delete=models.CASCADE, related_name="allergies")
    libelle = models.CharField(max_length=200)
    severite = models.CharField(max_length=10, choices=Severite.choices, default=Severite.MODEREE)
    signalee_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "allergie"

    def __str__(self) -> str:
        return f"{self.patient} — {self.libelle}"


class Consultation(models.Model):
    episode = models.ForeignKey(
        "episodes.EpisodeDeSoins", on_delete=models.CASCADE, related_name="consultations"
    )
    medecin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="consultations")
    date = models.DateTimeField(auto_now_add=True)

    # Triage / constantes.
    temperature_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    tension_arterielle_systolique = models.PositiveSmallIntegerField(null=True, blank=True)
    tension_arterielle_diastolique = models.PositiveSmallIntegerField(null=True, blank=True)
    frequence_cardiaque = models.PositiveSmallIntegerField(null=True, blank=True)
    frequence_respiratoire = models.PositiveSmallIntegerField(null=True, blank=True)
    poids_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    motif = models.CharField(max_length=255)
    anamnese = models.TextField(blank=True)
    examen_clinique = models.TextField(blank=True)
    conclusion = models.TextField(blank=True)

    modele_utilise = models.CharField(
        max_length=100, blank=True, help_text="Modèle de consultation par motif fréquent (Should)."
    )

    class Meta:
        verbose_name = "consultation"
        indexes = [models.Index(fields=["episode", "-date"], name="idx_consult_episode_date")]
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"Consultation {self.episode.numero} du {self.date:%Y-%m-%d}"


class Diagnostic(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name="diagnostics")
    code_cim11 = models.ForeignKey(DiagnosticCIM11, on_delete=models.PROTECT)
    principal = models.BooleanField(default=True)
    commentaire = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "diagnostic"

    def __str__(self) -> str:
        return f"{self.consultation} — {self.code_cim11}"
