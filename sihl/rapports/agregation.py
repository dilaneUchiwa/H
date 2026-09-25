"""
Agrégats pour le district sanitaire (chapitre 4.6.1).

Calculés comme sous-produit automatique des données transactionnelles,
jamais par saisie spécifique. Seuls des agrégats sont transmis par défaut
(jamais de données individuelles), conformément au principe de traçabilité
et de protection des données personnelles.
"""

from __future__ import annotations

import datetime

from django.db.models import Count, Sum
from django.utils import timezone

from sihl.consultations.models import Consultation, Diagnostic
from sihl.episodes.models import EpisodeDeSoins
from sihl.facturation.models import Paiement
from sihl.hospitalisation.models import Sejour


def rapport_mensuel(annee: int, mois: int) -> dict:
    debut = timezone.make_aware(datetime.datetime(annee, mois, 1))
    annee_fin, mois_fin = (annee + 1, 1) if mois == 12 else (annee, mois + 1)
    fin = timezone.make_aware(datetime.datetime(annee_fin, mois_fin, 1))

    consultations = Consultation.objects.filter(date__gte=debut, date__lt=fin)
    episodes = EpisodeDeSoins.objects.filter(date_ouverture__gte=debut, date_ouverture__lt=fin)
    sejours = Sejour.objects.filter(date_admission__gte=debut, date_admission__lt=fin)
    paiements = Paiement.objects.filter(date__gte=debut, date__lt=fin)

    diagnostics_frequents = (
        Diagnostic.objects.filter(consultation__date__gte=debut, consultation__date__lt=fin)
        .values("code_cim11__code", "code_cim11__libelle")
        .annotate(nombre=Count("id"))
        .order_by("-nombre")[:10]
    )

    return {
        "periode": {"annee": annee, "mois": mois},
        "nombre_consultations": consultations.count(),
        "nombre_episodes_ouverts": episodes.count(),
        "nombre_admissions": sejours.count(),
        "nombre_sorties": sejours.exclude(date_sortie__isnull=True).count(),
        "recettes_totales": paiements.aggregate(total=Sum("montant"))["total"] or 0,
        "diagnostics_frequents": list(diagnostics_frequents),
    }
