"""
Module M1 — Identification (chapitre 3.5.1, 3.7).

Décisions structurantes reprises du mémoire :
- Un patient = un IPP, jamais réattribué.
- `cle_phonetique` est une dénormalisation (Tableau 11), calculée à
  l'écriture uniquement, jamais modifiée manuellement (cf. save()).
- Aucune fusion automatique : la fusion est toujours un acte humain
  journalisé (voir `services.fusionner_patients`).
"""

from __future__ import annotations

from django.conf import settings
from django.db import models

from .ipp import generer_ipp
from .phonetique import cle_phonetique


class Patient(models.Model):
    class Sexe(models.TextChoices):
        MASCULIN = "M", "Masculin"
        FEMININ = "F", "Féminin"
        INDETERMINE = "I", "Indéterminé"

    ipp = models.CharField(max_length=20, unique=True, editable=False, db_index=True)
    annee_creation = models.PositiveSmallIntegerField(editable=False)

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField(null=True, blank=True)
    date_naissance_estimee = models.BooleanField(
        default=False, help_text="Âge souvent estimé : cf. tolérance en détection de doublons."
    )
    sexe = models.CharField(max_length=1, choices=Sexe.choices, default=Sexe.INDETERMINE)
    telephone = models.CharField(max_length=30, blank=True, db_index=True)
    adresse = models.CharField(max_length=255, blank=True)

    # Dénormalisation Tableau 11 : lecture seule côté application.
    cle_phonetique = models.CharField(max_length=32, editable=False, db_index=True, blank=True)

    actif = models.BooleanField(default=True)
    fusionne_vers = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="fiches_absorbees"
    )

    cree_le = models.DateTimeField(auto_now_add=True)
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="patients_crees"
    )

    class Meta:
        verbose_name = "patient"
        indexes = [
            models.Index(fields=["nom", "prenom"], name="idx_patient_nom_prenom"),
            models.Index(fields=["telephone"], name="idx_patient_telephone"),
            models.Index(fields=["cle_phonetique"], name="idx_patient_cle_phon"),
        ]

    def __str__(self) -> str:
        return f"{self.ipp} — {self.nom} {self.prenom}"

    def save(self, *args, **kwargs):
        # cle_phonetique est calculée ici et nulle part ailleurs (Tableau 11).
        self.cle_phonetique = cle_phonetique(self.nom)
        if not self.ipp:
            self._attribuer_ipp()
        super().save(*args, **kwargs)

    def _attribuer_ipp(self) -> None:
        from django.utils import timezone

        from .models import Patient as _Patient  # évite l'import circulaire au chargement

        annee = timezone.now().year
        code_etablissement = self._code_etablissement()
        dernier = (
            _Patient.objects.filter(annee_creation=annee)
            .exclude(ipp="")
            .order_by("-id")
            .first()
        )
        sequence = 1
        if dernier is not None:
            try:
                sequence = int(dernier.ipp.split("-")[2]) + 1
            except (IndexError, ValueError):
                sequence = _Patient.objects.filter(annee_creation=annee).count() + 1
        self.annee_creation = annee
        self.ipp = generer_ipp(code_etablissement, annee, sequence)

    @staticmethod
    def _code_etablissement() -> str:
        from django.conf import settings

        try:
            from sihl.core.models import ParametreEtablissement

            return ParametreEtablissement.charger().code_etablissement
        except Exception:
            return settings.CODE_ETABLISSEMENT


class CorrespondanceGraphie(models.Model):
    """
    Table locale de correspondance des graphies alternatives d'un même nom
    (chapitre 3.7.2), alimentée au fil de l'eau par les agents d'accueil.
    Ex. "Mohamed" / "Mohammed" / "Muhammad".
    """

    graphie = models.CharField(max_length=100, db_index=True)
    graphie_canonique = models.CharField(max_length=100, db_index=True)

    class Meta:
        verbose_name = "correspondance de graphie"
        unique_together = ("graphie", "graphie_canonique")

    def __str__(self) -> str:
        return f"{self.graphie} → {self.graphie_canonique}"


class FusionPatient(models.Model):
    """
    Journalise chaque fusion de fiches (chapitre 3.7.3). Réversible pendant
    ``ParametreEtablissement.fusion_reversibilite_jours`` (défaut 90 jours,
    DECISIONS.md #8).
    """

    patient_absorbe = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="fusions_en_tant_qu_absorbe"
    )
    patient_cible = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="fusions_en_tant_que_cible"
    )
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    effectuee_le = models.DateTimeField(auto_now_add=True)
    annulee = models.BooleanField(default=False)
    annulee_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "fusion de patients"
        ordering = ["-effectuee_le"]

    def __str__(self) -> str:
        return f"{self.patient_absorbe.ipp} → {self.patient_cible.ipp}"

    def reversible(self) -> bool:
        from datetime import timedelta

        from django.utils import timezone

        from sihl.core.models import ParametreEtablissement

        delai = ParametreEtablissement.charger().fusion_reversibilite_jours
        return not self.annulee and timezone.now() <= self.effectuee_le + timedelta(days=delai)
