"""
EpisodeDeSoins — entité intermédiaire obligatoire entre patient et
consultation (chapitre 3.5.1) : porte la facturation et l'agrégation d'actes.

`montant_du` et `montant_paye` sont des dénormalisations du Tableau 11,
maintenues **uniquement** par les triggers PostgreSQL définis dans la
migration `0002_triggers_denormalisation` de l'app `facturation`
(déclenchés sur ACTE et PAIEMENT). Ces deux colonnes sont en lecture
seule côté application : ne jamais les modifier ici.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models


class EpisodeDeSoins(models.Model):
    class Type(models.TextChoices):
        AMBULATOIRE = "AMBULATOIRE", "Ambulatoire"
        HOSPITALISATION = "HOSPITALISATION", "Hospitalisation"
        URGENCE = "URGENCE", "Urgence"

    class Statut(models.TextChoices):
        OUVERT = "OUVERT", "Ouvert"
        CLOTURE = "CLOTURE", "Clôturé"

    numero = models.CharField(max_length=30, unique=True, editable=False)
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="episodes")
    type_episode = models.CharField(max_length=20, choices=Type.choices, default=Type.AMBULATOIRE)
    statut = models.CharField(max_length=10, choices=Statut.choices, default=Statut.OUVERT)
    date_ouverture = models.DateTimeField(auto_now_add=True)
    date_fermeture = models.DateTimeField(null=True, blank=True)
    ouvert_par = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)

    # Dénormalisations Tableau 11 — écriture réservée aux triggers DB.
    montant_du = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    montant_paye = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)

    class Meta:
        verbose_name = "épisode de soins"
        indexes = [
            models.Index(fields=["patient", "-date_ouverture"], name="idx_episode_patient_date"),
        ]
        ordering = ["-date_ouverture"]

    def __str__(self) -> str:
        return self.numero

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self._generer_numero()
        super().save(*args, **kwargs)

    def _generer_numero(self) -> str:
        from django.utils import timezone

        annee = timezone.now().year
        compteur = EpisodeDeSoins.objects.filter(numero__startswith=f"EP-{annee}-").count() + 1
        return f"EP-{annee}-{compteur:06d}"

    def solde(self):
        return self.montant_du - self.montant_paye
