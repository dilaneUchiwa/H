"""
Administration, habilitation (RBAC) et traçabilité — Module M8.

Le mémoire (chapitre 3.9, Tableau 14) demande une matrice de droits par rôle
et exige que la journalisation (`JournalAudit`) soit une classe du domaine à
part entière, pas un simple log technique : elle est donc modélisée ici avec
ses propres règles (écriture seule côté application).
"""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class Permission(models.Model):
    """Droit unitaire, ex. ``patients.creer``, ``caisse.encaisser``."""

    code = models.CharField(max_length=100, unique=True)
    libelle = models.CharField(max_length=200)

    class Meta:
        verbose_name = "permission"
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code


class Role(models.Model):
    """
    Rôle métier (Tableau 14) : accueil, médecin, infirmier, laborantin,
    pharmacien, caissier, gestionnaire de lits, direction, administrateur
    système, référent technique.

    Règle du mémoire : l'administrateur système n'a jamais accès au contenu
    clinique (aucune permission ``clinique.*`` ne doit lui être attribuée en
    fixtures/paramétrage) ; laboratoire et pharmacie n'ont qu'un accès
    partiel au dossier (permissions dédiées, pas ``dossier.lecture_complete``).
    """

    code = models.SlugField(max_length=50, unique=True)
    libelle = models.CharField(max_length=100)
    permissions = models.ManyToManyField(Permission, blank=True, related_name="roles")
    acces_contenu_clinique = models.BooleanField(
        default=False,
        help_text="Doit rester False pour le rôle administrateur système.",
    )

    class Meta:
        verbose_name = "rôle"
        ordering = ["libelle"]

    def __str__(self) -> str:
        return self.libelle


class Utilisateur(AbstractUser):
    """
    Compte nominatif. Les comptes partagés sont proscrits par construction :
    ``username`` est unique et l'authentification est individuelle.
    """

    roles = models.ManyToManyField(Role, blank=True, related_name="utilisateurs")
    telephone = models.CharField(max_length=30, blank=True)
    service_rattachement = models.ForeignKey(
        "hospitalisation.Service", null=True, blank=True, on_delete=models.SET_NULL
    )
    echecs_authentification = models.PositiveSmallIntegerField(default=0)
    verrouille_jusqu_a = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "utilisateur"

    def a_la_permission(self, code: str) -> bool:
        if self.is_superuser:
            return True
        return Permission.objects.filter(code=code, roles__utilisateurs=self).exists()


class ParametreEtablissement(models.Model):
    """
    Paramétrage local de l'établissement (M8). Modèle singleton : une seule
    ligne exploitée par l'application (``ParametreEtablissement.charger()``).
    """

    nom_etablissement = models.CharField(max_length=200)
    code_etablissement = models.CharField(max_length=3)
    fusion_reversibilite_jours = models.PositiveIntegerField(
        default=90,
        help_text="Durée pendant laquelle une fusion de fiches patient reste réversible.",
    )

    class Meta:
        verbose_name = "paramètres de l'établissement"

    def __str__(self) -> str:
        return self.nom_etablissement

    @classmethod
    def charger(cls) -> "ParametreEtablissement":
        from django.conf import settings

        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "nom_etablissement": "Établissement",
                "code_etablissement": settings.CODE_ETABLISSEMENT,
                "fusion_reversibilite_jours": settings.FUSION_PATIENT_REVERSIBILITE_JOURS,
            },
        )
        return obj


class JournalAudit(models.Model):
    """
    Trace inaltérable des opérations sensibles (chapitre 3.9). Alimentée
    exclusivement par ``enregistrer()`` depuis chaque opération métier
    sensible — jamais par écriture directe ailleurs dans le code.

    Aucune méthode de mise à jour ou de suppression n'est exposée : la table
    est en écriture seule côté application (les migrations restent seules
    habilitées à la faire évoluer).
    """

    horodatage = models.DateTimeField(auto_now_add=True, db_index=True)
    auteur = models.ForeignKey(
        Utilisateur, null=True, on_delete=models.SET_NULL, related_name="operations_journalisees"
    )
    entite = models.CharField(max_length=100, help_text="Nom du modèle concerné, ex. Patient")
    entite_id = models.CharField(max_length=64)
    action = models.CharField(max_length=50, help_text="creation, modification, fusion, annulation, ...")
    valeurs_avant = models.JSONField(null=True, blank=True)
    valeurs_apres = models.JSONField(null=True, blank=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "entrée de journal d'audit"
        ordering = ["-horodatage"]
        indexes = [models.Index(fields=["entite", "entite_id"])]

    def __str__(self) -> str:
        return f"{self.horodatage} {self.auteur} {self.action} {self.entite}#{self.entite_id}"

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ValueError("JournalAudit est en écriture seule : aucune modification autorisée.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("JournalAudit est en écriture seule : aucune suppression autorisée.")

    @classmethod
    def enregistrer(
        cls,
        *,
        auteur,
        entite: str,
        entite_id,
        action: str,
        valeurs_avant: dict | None = None,
        valeurs_apres: dict | None = None,
        adresse_ip: str | None = None,
    ) -> "JournalAudit":
        return cls.objects.create(
            auteur=auteur,
            entite=entite,
            entite_id=str(entite_id),
            action=action,
            valeurs_avant=valeurs_avant,
            valeurs_apres=valeurs_apres,
            adresse_ip=adresse_ip,
        )
