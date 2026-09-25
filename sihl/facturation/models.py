"""
Module M5 — Caisse et facturation (chapitre 3.5.1, Tableau 11).

`EpisodeDeSoins.montant_du` / `montant_paye` sont maintenus par le trigger
PostgreSQL de `migrations/0002_trigger_montants_episode.py`, déclenché sur
`ActeFacturable` et `Paiement` — jamais par le code applicatif ici.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class TarifActe(models.Model):
    """Nomenclature/tarifs (table de paramétrage, ⚠️ À DÉCIDER #4)."""

    code = models.SlugField(max_length=30, unique=True)
    libelle = models.CharField(max_length=200)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "tarif d'acte"
        ordering = ["libelle"]

    def __str__(self) -> str:
        return f"{self.libelle} ({self.montant})"


class ActeFacturable(models.Model):
    episode = models.ForeignKey(
        "episodes.EpisodeDeSoins", on_delete=models.PROTECT, related_name="actes_factures"
    )
    tarif = models.ForeignKey(TarifActe, on_delete=models.PROTECT)
    quantite = models.PositiveIntegerField(default=1)
    montant = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    exoneration = models.BooleanField(default=False)
    motif_exoneration = models.CharField(max_length=255, blank=True)
    facture_le = models.DateTimeField(auto_now_add=True)
    facture_par = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "acte facturable"
        ordering = ["-facture_le"]

    def __str__(self) -> str:
        return f"{self.tarif} x{self.quantite} — {self.episode.numero}"

    def save(self, *args, **kwargs):
        montant_unitaire = 0 if self.exoneration else self.tarif.montant
        self.montant = montant_unitaire * self.quantite
        super().save(*args, **kwargs)


class Paiement(models.Model):
    class ModePaiement(models.TextChoices):
        ESPECES = "ESPECES", "Espèces"
        MOBILE_MONEY = "MOBILE_MONEY", "Monnaie électronique"
        AUTRE = "AUTRE", "Autre"

    episode = models.ForeignKey("episodes.EpisodeDeSoins", on_delete=models.PROTECT, related_name="paiements")
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    mode = models.CharField(max_length=15, choices=ModePaiement.choices, default=ModePaiement.ESPECES)

    # Reçu numéroté par plage pré-attribuée (chapitre 5.3, mode dégradé
    # hors-ligne) : numéro fourni par le service de séquence, jamais
    # généré côté client sans plage pré-attribuée.
    numero_recu = models.CharField(max_length=30, unique=True, editable=False)

    date = models.DateTimeField(auto_now_add=True)
    encaisse_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "paiement"
        indexes = [models.Index(fields=["date", "encaisse_par"], name="idx_paiement_date_user")]
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"Reçu {self.numero_recu} — {self.montant}"

    def save(self, *args, **kwargs):
        if not self.numero_recu:
            self.numero_recu = self._prochain_numero_recu()
        super().save(*args, **kwargs)

    @staticmethod
    def _prochain_numero_recu() -> str:
        from django.utils import timezone

        annee = timezone.now().year
        compteur = Paiement.objects.filter(numero_recu__startswith=f"RECU-{annee}-").count() + 1
        return f"RECU-{annee}-{compteur:07d}"


class JournalCaisse(models.Model):
    """Journal de caisse + rapprochement quotidien (M5)."""

    date_cloture = models.DateField(unique=True)
    montant_theorique = models.DecimalField(max_digits=12, decimal_places=2)
    montant_compte = models.DecimalField(max_digits=12, decimal_places=2)
    ecart = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    cloture_par = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    cloture_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "journal de caisse"
        ordering = ["-date_cloture"]

    def save(self, *args, **kwargs):
        self.ecart = self.montant_compte - self.montant_theorique
        super().save(*args, **kwargs)
